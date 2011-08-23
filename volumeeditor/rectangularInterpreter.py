# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt






class RectangularInterpreter(QObject):

    def __init__(self, rectangularModel):
        QObject.__init__(self, parent=None)
        self._rectangularModel = rectangularModel
    
            
    def onMouseMove(self,pos):
        print "on mouse Move"
        self._rectangularModel.moveTo(pos)

    def onLeftMouseButtonPress(self,pos, shape):
        print "on left Mouse Button Pressed"
        self._rectangularModel.beginSelecting(pos)       
        
    def onMouseButtonRelease(self,pos):
        print "on Mouse Button Release"
        self._rectangularModel.endSelecting(pos)
        
    def onWheel(self,delta,axis):
        print "rectangular selection is enabled"

    def onMouseButtonDblClick(self,x,y,axis):
        print "rectangular selection is enabled"
        