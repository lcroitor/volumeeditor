# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt, pyqtSignal

#*******************************************************************************
# C r o s s h a i r C o n t r o l e r                                          *
#*******************************************************************************

class CrosshairControler(QObject):
    def __init__(self, brushingModel, imageViews):
        QObject.__init__(self, parent=None)
        self._brushingModel = brushingModel
        self._brushingModel.brushSizeChanged.connect(self._setBrushSize)
        self._brushingModel.brushColorChanged.connect(self._setBrushColor)
    
    def _setBrushSize(self):
        pass
    
    def _setBrushColor(self):
        pass
        
#*******************************************************************************
# B r u s h i n g C o n t r o l e r                                            *
#*******************************************************************************

class BrushingControler(QObject):
    def __init__(self, brushingModel, positionModel, dataSink):
        QObject.__init__(self, parent=None)
        self._dataSink = dataSink
        
        self._brushingModel = brushingModel
        self._brushingModel.brushStrokeAvailable.connect(self._writeIntoSink)
        self._positionModel = positionModel
        
    def _writeIntoSink(self, brushStrokeOffset, labels):
        activeView = self._positionModel.activeView
        slicingPos = self._positionModel.slicingPos
        t, c       = self._positionModel.time, self._positionModel.channel
        
        slicing = [slice(brushStrokeOffset.x(), brushStrokeOffset.x()+labels.shape[0]), \
                   slice(brushStrokeOffset.y(), brushStrokeOffset.y()+labels.shape[1])]
        slicing.insert(activeView, slicingPos[activeView])
        slicing = (t,) + tuple(slicing) + (c,)
        print "_writeIntoSink", slicing, labels.shape, labels
        
        self._dataSink.put(slicing, labels)
        
#*******************************************************************************
# B r u s h i n g I n t e r p r e t e r                                        *
#*******************************************************************************

class BrushingInterpreter(QObject):

    def __init__(self, brushingModel, imageViews):
        QObject.__init__(self, parent=None)
        self._imageViews = imageViews
        self._brushingModel = brushingModel
        self._brushDown = False

    def onMouseMove(self,pos):
        if self._brushDown:
            self._brushingModel.moveTo(pos)

    def onLeftMouseButtonPress(self,pos, shape):
        self._brushDown = True
        #print 'calling begin drawing with pos=%r' % (pos,)
        self._brushingModel.beginDrawing(pos, shape)       
        
    def onMouseButtonRelease(self,pos):
        self._brushingModel.endDrawing(pos)
        self._brushDown = False
        
    def onWheel(self,delta,axis):
        print "brushing is not enabled"

    def onMouseButtonDblClick(self,x,y,axis):
        print "brushing is not enabled"
        
    
        
    
