#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2010, 2011 C Sommer, C Straehle, U Koethe, FA Hamprecht. All rights reserved.
#    
#    Redistribution and use in source and binary forms, with or without modification, are
#    permitted provided that the following conditions are met:
#    
#       1. Redistributions of source code must retain the above copyright notice, this list of
#          conditions and the following disclaimer.
#    
#       2. Redistributions in binary form must reproduce the above copyright notice, this list
#          of conditions and the following disclaimer in the documentation and/or other materials
#          provided with the distribution.
#    
#    THIS SOFTWARE IS PROVIDED BY THE ABOVE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESS OR IMPLIED
#    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#    FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE ABOVE COPYRIGHT HOLDERS OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#    ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#    
#    The views and conclusions contained in the software and documentation are those of the
#    authors and should not be interpreted as representing official policies, either expressed
#    or implied, of their employers.

from functools import partial
from PyQt4.QtCore import QRect, QRectF, QTimer, pyqtSignal, QMutex
from PyQt4.QtGui import QGraphicsScene, QImage
from PyQt4.QtOpenGL import QGLWidget
from OpenGL.GL import GL_CLAMP_TO_EDGE, GL_COLOR_BUFFER_BIT, GL_DEPTH_TEST, \
                      GL_NEAREST, GL_QUADS, GL_TEXTURE_2D, \
                      GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, \
                      GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, \
                      glBegin, glEnd, glBindTexture, glClearColor, glDisable, \
                      glEnable, glRectf, glClear, glTexCoord2f, \
                      glTexParameteri, glVertex2f, glColor4f

from patchAccessor import PatchAccessor
from imageSceneRendering import ImageSceneRenderThread

#*******************************************************************************
# I m a g e P a t c h                                                          *
#*******************************************************************************

class ImagePatch(object):    
    """
    A tile/patch that makes up the whole 2D scene as displayed in ImageScene2D.
   
    An ImagePatch has a bounding box (self.rect, self.rectF) and
    its image content is either represented by a QImage (in software rendering)
    or via an OpenGL texture.
    
    When the current image content becomes invalid or is currently
    being overwritten, the patch becomes dirty.
    """ 
    
    def __init__(self, rectF):
        assert(type(rectF) == QRectF)
        
        self.rectF  = rectF
        self.rect   = QRect(round(rectF.x()),     round(rectF.y()), \
                            round(rectF.width()), round(rectF.height()))
        self._image  = QImage(self.rect.width(), self.rect.height(), QImage.Format_ARGB32_Premultiplied)
        self.texture = -1
        self.dirty = True
        self.mutex = QMutex()

    @property
    def height(self):
        return self.rect.height()
    
    @property
    def width(self):
        return self.rect.width()

    def drawTexture(self):
        """
        Renders the current context as a texture. 
        Precondition: OpenGL mode and OpenGL context active.
        """
        
        tx = self.rect.x()
        ty = self.rect.y()
        w = self.rect.width()
        h = self.rect.height()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(tx, ty)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(tx + w, ty)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(tx + w, ty + h)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(tx, ty + h)
        glEnd()

    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self, img):
        self._image = img
        self.dirty = False

#*******************************************************************************
# I m a g e S c e n e 2 D                                                      *
#*******************************************************************************

class ImageScene2D(QGraphicsScene):
    """
    The 2D scene description of a tiled image generated by evaluating
    an overlay stack, together with a 2D cursor.
    """
    
    # base patch size: blockSize x blockSize
    blockSize = 128
    # overlap between patches 
    # positive number prevents rendering artifacts between patches for certain zoom levels
    # increases the base blockSize 
    overlap = 1 
    
    # update delay when a new patch arrives in ms
    glUpdateDelay = 10
    
    @property
    def stackedImageSources(self):
        return self._stackedImageSources
    
    @stackedImageSources.setter
    def stackedImageSources(self, s):
        self._stackedImageSources = s
        s.isDirty.connect(self._invalidateRect)
        self._initializePatches()
        #s.stackChanged.connect(self._initializePatches)
        s.stackChanged.connect(partial(self._invalidateRect, QRect()))

    @property
    def shape(self):
        return (self.sceneRect().width(), self.sceneRect().height())
    @shape.setter
    def shape(self, shape2D):
        assert len(shape2D) == 2
        self.setSceneRect(0,0, *shape2D)
        
        del self._renderThread
        del self.imagePatches
        
        self._patchAccessor = PatchAccessor(self.shape[1], self.shape[0], blockSize=self.blockSize)
        self.imagePatches = [[] for i in range(self._patchAccessor.patchCount)]
            
        self._renderThread = ImageSceneRenderThread(self.imagePatches, self.stackedImageSources, parent=self)
        self._renderThread.start()
        self._renderThread.patchAvailable.connect(self._schedulePatchRedraw)
        
        self._initializePatches()
    
    def __init__( self ):
        QGraphicsScene.__init__(self)
        self._glWidget = None
        self._useGL = False
        self._updatableTiles = []

        # tile rendering
        self.imagePatches = None
        self._renderThread = None
        self._stackedImageSources = None
        self._numLayers = 0 #current number of 'layers'
    
        def cleanup():
            self._renderThread.stop()
        self.destroyed.connect(cleanup)

    def activateOpenGL( self, qglwidget ):
        self._useGL = True
        self._glWidget = qglwidget

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glClearColor(0.0, 0.0, 0.0, 0.0);
        glClear(GL_COLOR_BUFFER_BIT)

    def deactivateOpenGL( self ):
        self._useGL = False
        self._glWidget = None
    
    def _initializePatches(self):
        if self.stackedImageSources is None or self.shape == (0.0, 0.0):
            return
        
        if len(self.stackedImageSources) != self._numLayers:
            self._numLayers = len(self.stackedImageSources)
            #add an additional layer for the final composited image patch
            for i in range(self._patchAccessor.patchCount):
                r = self._patchAccessor.patchRectF(i, self.overlap)
                patches = [ImagePatch(r) for j in range(self._numLayers+1)]
                self.imagePatches[i] = patches
    

    def _invalidateRect(self, rect = QRect()):
        if not rect.isValid():
            #everything is invalidated
            #we cancel all requests
            self._renderThread.cancelAll()
            self._updatableTiles = []
        
        if self._stackedImageSources is not None and self._numLayers != len(self._stackedImageSources):
            self._initializePatches()
        
        for i,patch in enumerate(self.imagePatches):
            if not rect.isValid() or rect.intersects(patch[self._numLayers].rect):
                ##convention: if a rect is invalid, it is infinitely large
                patch[self._numLayers].dirty = True
                self._schedulePatchRedraw(i)

    def _schedulePatchRedraw(self, patchNr):
        p = self.imagePatches[patchNr][self._numLayers]
        self._updatableTiles.append(patchNr)
        if not self._useGL:
            self.invalidate(p.rectF, QGraphicsScene.BackgroundLayer)
        else:
            QTimer.singleShot(self.glUpdateDelay, self.update)

    def drawBackgroundSoftware(self, painter, rect):
        drawnTiles = 0
        for patches in self.imagePatches:
            patch = patches[self._numLayers]
            if not patch.rectF.intersect(rect): continue
            patch.mutex.lock()
            painter.drawImage(patch.rectF.topLeft(), patch.image)
            patch.mutex.unlock()
            drawnTiles +=1
        #print "ImageView2D.drawBackgroundSoftware: drew %d of %d tiles" % (drawnTiles, len(self.imagePatches)) 
    
    def drawBackgroundGL(self, painter, rect):
        painter.beginNativePainting()
        
        #This will clear the screen, but also introduce flickering
        glClearColor(0.0, 1.0, 0.0, 1.0);
        glClear(GL_COLOR_BUFFER_BIT);
        
        #update the textures of those patches that were updated
        for t in self._updatableTiles:
            patch = self.imagePatches[t][self._numLayers]
            if patch.texture > -1:
                self._glWidget.deleteTexture(patch.texture)
            patch.texture = self._glWidget.bindTexture(patch.image)
            #see 'backingstore' example by Ariya Hidayat
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            #this ensures a seamless transition between tiles
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        self._updatableTiles = []
        
        drawnTiles = 0
        for patches in self.imagePatches:
            patch = patches[self._numLayers]
            if not patch.rectF.intersect(rect): continue
            patch.drawTexture()
            drawnTiles +=1

        #print "ImageView2D.drawBackgroundGL: drew %d of %d tiles" % (drawnTiles, len(self.imagePatches))
        painter.endNativePainting()

    def drawBackground(self, painter, rect):
        #Abandon previous workloads
        #FIXME FIXME
        #self._renderThread.queue.clear()
        #self._renderThread.newerDataPending.set()

        #Find all patches that intersect the given 'rect'.
        for i,patch in enumerate(self.imagePatches):
            patch = patch[self._numLayers]
            if patch.dirty and rect.intersects(patch.rectF):
                self._renderThread.requestPatch(i)
        
        if self._useGL:
            self.drawBackgroundGL(painter, rect)
        else:
            self.drawBackgroundSoftware(painter, rect)
