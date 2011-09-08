# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject, QPointF, QRectF
from PyQt4.QtCore import Qt
from PyQt4.QtGui  import  QPen, QBrush, QGraphicsRectItem, QPainter, QImage


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
        self.activeItem = None
        #self.currentRect = QRectF()
        self._rectangularModel.rectangleChanged.connect(self.updateSceneRect)


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
            
            
        print 'self.x', self.x
        print 'self.y', self.y
        print 'self.width', self.width
        print 'self.height', self.height
        print 'activeView.sceneRect().width()', activeView.sceneRect().width()
        print 'activeView.sceneRect().height()', activeView.sceneRect().height()
        
        #make sure that the rectangle does not extend past the drawing area
        if self.x + self.width > activeView.sceneRect().width():
            self.width = activeView.sceneRect().width() - self.x
        if self.y + self.height > activeView.sceneRect().height():
            self.height = activeView.sceneRect().height() - self.y
        if self.x > activeView.sceneRect().width():
            self.widht = self.x - activeView.sceneRect().width()
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0

        itemOne = QGraphicsRectItem(self.x,self.y,self.width, self.height)
        itemOne.setPen(self.pen)
        itemOne.setBrush(self.brush)
        #activeView.fitInView(itemOne, mode = Qt.IgnoreAspectRatio)
        activeView.scene().addItem(itemOne)
        print 'activeView.scene()', activeView.scene()
        '''
        self.activeItem = itemAt(self.x,self.y) 
        if itemOne == self.activeItem:
            self.qDebug() 
            print  "You clicked on item", itemOne
        else:
            self.qDebug() 
            print  "You didn't click on an item", itemOne
 
        def itemAt(self, x,y):
            pos = (x, y)
            return pos
        '''    
        itemOne.show()

        
