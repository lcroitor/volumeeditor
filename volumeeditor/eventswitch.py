# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject, QEvent, Qt, pyqtSignal
from PyQt4.QtGui import QApplication



from imageView2D import ImageView2D
from positionModel import PositionModel
from navigationControler import NavigationControler, NavigationInterpreter
from brushingcontroler import BrushingControler, BrushingInterpreter
from functools import partial
from PyQt4.QtCore import SIGNAL



class EventSwitch(QObject):
    def __init__( self, imageviews,currentInterpreter):
        super(EventSwitch, self).__init__()
        for view in imageviews:
            print "INSTALLING EVENT FILTER ON VIEWPORT"
            view.viewport().installEventFilter( self )
        self._imageViews = imageviews
        self._currentInterpreter=currentInterpreter
        self._disabled = True
 
    
    def setInterpreter(self, currentInterpreter):
        if self._currentInterpreter is not currentInterpreter:
            self._currentInterpreter=currentInterpreter
            
    
        
    def toggle(self):
        self._disabled = not self._disabled
    
        
    def eventFilter( self, watched, event ):
        imageView = watched.parent()
        if self._disabled:
            return False
        
        for i in range(3):
            x = self._imageViews[i]
            if x == imageView:
                break
        x, y = imageView.x, imageView.y
        
        if event.type()==QEvent.Wheel:
            print "###################################"
            keys = QApplication.keyboardModifiers()
            k_alt = (keys == Qt.AltModifier)
            for i in range(3):
                
                if event.delta() > 0:
                    if k_alt:
                        self._currentInterpreter.onWheel(10,axis=i)
                    else:
                        self._currentInterpreter.onWheel(1,axis=i)
                else:
                    if k_alt:
                        self._currentInterpreter.onWheel(-10,axis=i)
                    else:
                        self._currentInterpreter.onWheel(-1,axis=i)

            return True
        
        if event.type()==QEvent.MouseButtonDblClick:
            for i in range(3):
                self._currentInterpreter.onMouseButtonDblClick(x,y,axis=i)

            return True
            
        if event.type()==QEvent.MouseMove:
            pos = (x,y)
            self._currentInterpreter.onMouseMove(pos)
            return True

        if event.type()==QEvent.MouseButtonPress:
            pos = (x,y)
            shape = imageView.shape
            if event.buttons()==Qt.LeftButton:
                self._currentInterpreter.onLeftMouseButtonPress(pos, shape)
                return True
                            
        if event.type()==QEvent.MouseButtonRelease:
            pos = (x,y)
            self._currentInterpreter.onMouseButtonRelease(pos)
            return True
        
            

        return False

        
       
        
        
	    
