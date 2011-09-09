# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject, QPointF, QRectF
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPen, QBrush, QGraphicsRectItem, QImage, QPainter



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
        self._rectangularModel.beginSelecting(pos)
        
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
        self.activeItem = None
        self.currentSelectedRects = []
        self._rectangularModel.currentRectangleChanged.connect(self.updateSceneRect)

    def updateSceneRect(self, x, y, w, h):
        view = self._positionModel.activeView
        activeView = self._imageViews[view]
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        self.initialPos = (x, y)
        self.mapPos = activeView.scene().scene2data.map(QPointF(self.initialPos[0],self.initialPos[1] ))
        self.x,self.y= self.mapPos.x(), self.mapPos.y()
        self.widthHeight = (w, h)
        self.mapWidthHeight = activeView.scene().scene2data.map(QPointF(self.widthHeight[0],self.widthHeight[1]))
        self.width = self.mapWidthHeight.x()
        self.height = self.mapWidthHeight.y()
        #make sure that the rectangle does not extend past the drawing area
        if self.x + self.width > activeView.sceneRect().width():
            self.width = activeView.sceneRect().width() - self.x
        if self.y + self.height > activeView.sceneRect().height():
            self.height = activeView.sceneRect().height() - self.y
        if self.x > activeView.sceneRect().width():
            self.widht = self.x - activeView.sceneRect().width()

        activeView.scene().clear()
        rect = activeView.scene().addRect(self.x,self.y,self.width, self.height, self.pen, self.brush)
        rect.show()
