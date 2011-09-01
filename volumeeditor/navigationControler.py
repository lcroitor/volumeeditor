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

from PyQt4.QtCore import QObject, QTimer
from PyQt4.QtGui  import QColor

import  copy
from functools import partial

def posView2D(pos3d, axis):
    pos2d = copy.deepcopy(pos3d)
    """convert from a 3D position to a 2D position on the slicing plane
       perpendicular to axis"""
    del pos2d[axis]
    return pos2d

#*******************************************************************************
# N a v i g a t i o n I n t e r p r e t e r                                    *
#*******************************************************************************

class NavigationInterpreter(QObject):

    """
    Provides slots to listens to mouse/keyboard events from multiple
    slice views and interprets them as actions upon a N-D volume
    (whereas the individual ImageView2D/ImageScene2D know nothing about the
    data they display).
    
    After interpreting the user's events on these widgets, the position model
    is updated.
    """
    
    def __init__(self, model):
        """
        Constructs an interpreter which will update the
        PositionModel model.
        
        The user of this class needs to make the appropriate connections
        from the ImageView2D to the methods of this class from the outside 
        himself.
        """
        QObject.__init__(self)
        self._model = model
    
    def changeSliceRelative(self, delta, axis):
        """
        Change slice along a certain axis relative to current slice.

        delta -- add delta to current slice position [positive or negative int]
        axis  -- along which axis [0,1,2]
        """
        
        if delta == 0:
            return
        newSlice = self._model.slicingPos[axis] + delta
        if newSlice < 0 or newSlice >= self._model.volumeExtent(axis):
            return
        newPos = copy.copy(self._model.slicingPos)
        newPos[axis] = newSlice
        
        cursorPos = copy.copy(self._model.cursorPos)
        cursorPos[axis] = newSlice
        self._model.cursorPos  = cursorPos  

        self._model.slicingPos = newPos

    def changeSliceAbsolute(self, value, axis):
        """
        Change slice along a certain axis.

        value -- slice number
        axis  -- along which axis [0,1,2]
        """
        
        if value < 0 or value > self._model.volumeExtent(axis):
            return
        newPos = copy.copy(self._model.slicingPos)
        newPos[axis] = value
        if not self._positionValid(newPos):
            return
        
        cursorPos = copy.copy(self._model.cursorPos)
        cursorPos[axis] = value
        self._model.cursorPos  = cursorPos  
        
        self._model.slicingPos = newPos
        
    def sliceIntersectionIndicatorToggle(self, show):
        """
        Toggle the display of the slice intersection indicator lines
        to on/off according to `show`.
        """
        self.indicateSliceIntersection = show
    
    def positionCursor(self, x, y, axis):
        """
        Change position of the crosshair cursor.

        x,y  -- cursor position on a certain image scene
        axis -- perpendicular axis [0,1,2]
        """
        
        #we get the 2D coordinates x,y from the view that
        #shows the projection perpendicular to axis
        #set this view as active
        self._model.activeView = axis
        
        newPos = [x,y]
        newPos.insert(axis, self._model.slicingPos[axis])

        if newPos == self._model.cursorPos:
            return
        if not self._positionValid(newPos):
            return

        self._model.cursorPos = newPos

    def positionSlice(self, x, y, axis):
        newPos = copy.copy(self._model.slicingPos)
        i,j = posView2D([0,1,2], axis)
        newPos[i] = x
        newPos[j] = y
        if newPos == self._model.slicingPos:
            print "new pos"
            return
        if not self._positionValid(newPos):
            print "position valid"
            return
        
        self._model.slicingPos = newPos
        print "slicing pos"
    def _positionValid(self, pos):
        for i in range(3):
            if pos[i] < 0 or pos[i] >= self._model.shape[i]:
                return False
        return True
        
    def onMouseMove(self,pos):
        x,y = pos[0], pos[1]
        for i in range(3):
            self.positionCursor(x,y,axis=i)
    def onWheel(self,delta,axis):
        self.changeSliceRelative(delta,axis)
        
    def onMouseButtonDblClick(self,x,y,axis):
        print "on Mouse Button Double Click"
        self.positionSlice(x,y,axis)

    def onMouseButtonRelease(self,pos):
        print "navigation is not enabled"
        
    def onLeftMouseButtonPress(self,pos,shape):
        print "navigation is not enabled"
        
    
#*******************************************************************************
# N a v i g a t i o n C o n t r o l e r                                        *
#*******************************************************************************

class NavigationControler(QObject):
    """
    Controler for navigating through the volume.
    
    The NavigationContrler object listens to changes
    in a given PositionModel and updates three slice
    views (representing the spatial X, Y and Z slicings)
    accordingly.
    """
    
    ##
    ## properties
    ##e
    
    @property
    def axisColors( self ):
        return self._axisColors
    @axisColors.setter
    def axisColors( self, colors ):
        self._axisColors = colors
        self._views[0]._sliceIntersectionMarker.setColor(self.axisColors[1], self.axisColors[2])
        self._views[1]._sliceIntersectionMarker.setColor(self.axisColors[0], self.axisColors[2])
        self._views[2]._sliceIntersectionMarker.setColor(self.axisColors[0], self.axisColors[1])
        for axis, v in enumerate(self._views):
            #FIXME: Bad dependency here on hud to be available!
            if v.hud: v.hud.bgColor = self.axisColors[axis]
        
    @property
    def indicateSliceIntersection(self):
        return self._indicateSliceIntersection
    @indicateSliceIntersection.setter
    def indicateSliceIntersection(self, show):
        self._indicateSliceIntersection = show
        for v in self._views:
            v._sliceIntersectionMarker.setVisibility(show)
        
    def __init__(self, imageView2Ds, sliceSources, positionModel, time = 0, channel = 0, view3d=None):
        QObject.__init__(self)
        assert len(imageView2Ds) == 3

        # init fields
        self._views = imageView2Ds
        self._sliceSources = sliceSources
        self._model = positionModel
        self._beginStackIndex = 0
        self._endStackIndex   = 1
        self._view3d = view3d

        #FIXME
        #self._views[0].swapAxes()

        self.axisColors = [QColor(255,0,0,255), QColor(0,255,0,255), QColor(0,0,255,255)]
    
    def moveCrosshair(self, newPos, oldPos):
        self._updateCrossHairCursor()
    
    def moveSlicingPosition(self, newPos, oldPos):
        for i in range(3):
            if newPos[i] != oldPos[i]:
                self._updateSlice(self._model.slicingPos[i], i)
        self._updateSliceIntersection()
        
        #when scrolling fast through the stack, we don't want to update
        #the 3d view all the time
        if self._view3d is None:
            return
        def maybeUpdateSlice(oldSlicing):
            if oldSlicing == self._model.slicingPos:
                for i in range(3):
                    self._view3d.ChangeSlice(self._model.slicingPos[i], i)
        QTimer.singleShot(50, partial(maybeUpdateSlice, self._model.slicingPos))
                    
    def changeTime(self, newTime):
        for i in range(3):
            for src in self._sliceSources[i]:
                src.setThrough(0, newTime)
    
    def changeChannel(self, newChannel):
        for i in range(3):
            for src in self._sliceSources[i]:
                src.setThrough(2, newChannel)
    
    #private functions ########################################################
    
    def _updateCrossHairCursor(self):
        y,x = posView2D(self._model.cursorPos, axis=self._model.activeView)
        self._views[self._model.activeView]._crossHairCursor.showXYPosition(x,y)
        for i, v in enumerate(self._views):
            v._crossHairCursor.setVisible( self._model.activeView == i )
    
    def _updateSliceIntersection(self):
        for axis, v in enumerate(self._views):
            y,x = posView2D(self._model.slicingPos, axis)
            v._sliceIntersectionMarker.setPosition(x,y)

    def _updateSlice(self, num, axis):
        if num < 0 or num >= self._model.volumeExtent(axis):
            raise Exception("NavigationControler._setSlice(): invalid slice number = %d not in range [0,%d)" % (num, self._model.volumeExtent(axis)))
        #FIXME: Shouldnt the hud listen to the model changes itself?
        self._views[axis].hud.sliceSelector.setValue(num)

        #re-configure the slice source
        for src in self._sliceSources[axis]:
            src.setThrough(1, num)

