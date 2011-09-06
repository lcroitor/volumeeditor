# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject, QRectF, pyqtSignal,QPointF
from PyQt4.QtCore import Qt
from PyQt4.QtGui  import QWidget, QPen, QBrush, QColor, QGraphicsScene, QGraphicsRectItem,\
                         QImage, QPainter





class RectangularInterpreter(QObject):

    def __init__(self, rectangularModel):
        QObject.__init__(self, parent=None)
        self._rectangularModel = rectangularModel
        self._buttonDown = False
    
            
    def onMouseMove(self,pos):
        if self._buttonDown:
            self._rectangularModel.moveTo(pos)

    def onLeftMouseButtonPress(self,pos, shape):
        self._buttonDown = True
        print 'begin selecting with pos=%r' % (pos,)
        self._rectangularModel.beginSelecting(pos, shape)       
        
    def onMouseButtonRelease(self,pos):
        self._rectangularModel.endSelecting(pos)
        print 'ends selecting with pos=%r' % (pos,)
        self._buttonDown = False
        
    def onWheel(self,delta,axis):
        print "rectangular selection is not enabled"

    def onMouseButtonDblClick(self,x,y,axis):
        print "rectangular selection is not enabled"
        
# RECTANGULAR CONTROLER

class RectangularControler(QObject):

    def __init__(self, rectangularModel,positionModel, imageViews):
        QObject.__init__(self, parent=None)
        self._rectangularModel = rectangularModel
        self._positionModel = positionModel
        self._imageViews = imageViews
        self.pen=QPen(Qt.blue)
        self.brush=QBrush(Qt.Dense6Pattern)

    def updateSceneRect(self):
        view = self._positionModel.activeView
        activeView = self._imageViews[view]
        self.initialPos = (self._rectangularModel.rect.x, self._rectangularModel.rect.y)
        self.mapPos = activeView.scene().scene2data.map(QPointF(self.initialPos[0],self.initialPos[1] ))
        self.x,self.y= self.mapPos.x(), self.mapPos.y()
        self.widthHeight = (self._rectangularModel.rect.width, self._rectangularModel.rect.height)
        self.mapWidthHeight = activeView.scene().scene2data.map(QPointF(self.widthHeight[0],self.widthHeight[1]))
        self.width = self.mapWidthHeight.x()
        self.height = self.mapWidthHeight.y() 
        activeView.scene().clear()

        #make sure that the rectangle does not extend past the drawing area
        if self.x + self.width > activeView.sceneRect().width():
            self.width = activeView.sceneRect().width() - self.x
        if self.y + self.height > activeView.sceneRect().height():
            self.height = activeView.sceneRect().height() - self.y

        
        itemOne = QGraphicsRectItem(self.x,self.y,self.width, self.height)
        itemOne.setPen(self.pen)
        itemOne.setBrush(self.brush)
        activeView.scene().addItem(itemOne)
        itemOne.show()