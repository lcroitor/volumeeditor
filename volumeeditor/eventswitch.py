# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject, QEvent, Qt
from PyQt4.QtGui import QApplication



class EventSwitch(QObject):
    def __init__( self, imageviews,currentInterpreter):
        super(EventSwitch, self).__init__()
        for view in imageviews:
            print "INSTALLING EVENT FILTER ON VIEWPORT"
            view.viewport().installEventFilter( self )
        self._imageViews = imageviews
        self._currentInterpreter=currentInterpreter
        #self._disabled = True
 
    
    def setInterpreter(self, currentInterpreter):
        if self._currentInterpreter is not currentInterpreter:
            self._currentInterpreter=currentInterpreter
            

    def eventFilter( self, watched, event ):
        imageView = watched.parent()

        for i in range(3):
            x = self._imageViews[i]
            if x == imageView:
                break

        if event.type()==QEvent.Wheel:
            keys = QApplication.keyboardModifiers()
            k_alt = (keys == Qt.AltModifier)
            k_ctrl = (keys == Qt.ControlModifier)

            for i in range(3):
                
                if event.delta() > 0:
                    if k_alt:
                        self._currentInterpreter.onWheel(10,axis=i)
                    elif k_ctrl:
                        scaleFactor = 1.1
                        imageView.doScale(scaleFactor)
                    else:
                        self._currentInterpreter.onWheel(1,axis=i)
                else:
                    if k_alt:
                        self._currentInterpreter.onWheel(-10,axis=i)
                    elif k_ctrl:
                        scaleFactor = 0.9
                        imageView.doScale(scaleFactor)
                    else:
                        self._currentInterpreter.onWheel(-1,axis=i)

            return True
        
        if event.type()==QEvent.MouseButtonDblClick:
            self.mousePos = imageView.mapScene2Data(imageView.mapToScene(event.pos()))
            x = self.mousePos.x()
            y = self.mousePos.y()
            for i in range(3):
                self._currentInterpreter.onMouseButtonDblClick(x,y,axis=i)

            return True
            
        if event.type()==QEvent.MouseMove:
            self.mousePos = imageView.mapScene2Data(imageView.mapToScene(event.pos()))
            x = self.mousePos.x()
            y = self.mousePos.y()
            pos = (x,y)
            self._currentInterpreter.onMouseMove(pos)
            return True

        if event.type()==QEvent.MouseButtonPress:
            self.mousePos = imageView.mapScene2Data(imageView.mapToScene(event.pos()))
            x = self.mousePos.x()
            y = self.mousePos.y()
            pos = (x,y)
            shape = imageView.sliceShape
            if event.buttons()==Qt.LeftButton:
                self._currentInterpreter.onLeftMouseButtonPress(pos, shape)
                return True
                            
        if event.type()==QEvent.MouseButtonRelease:
            self.mousePos = imageView.mapScene2Data(imageView.mapToScene(event.pos()))
            x = self.mousePos.x()
            y = self.mousePos.y()
            pos = (x,y)
            self._currentInterpreter.onMouseButtonRelease(pos)
            return True
        
            

        return False


