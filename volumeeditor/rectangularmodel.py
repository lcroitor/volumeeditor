# -*- coding: utf-8 -*-


from PyQt4.QtCore import QObject, QThread, Qt, QSize, QPointF, QRectF,\
                         QRect, QPoint, QSizeF
from PyQt4.QtGui  import QWidget, QPen, QBrush, QColor, QGraphicsScene, QGraphicsRectItem,\
                         QImage, QPainter
                         
                         
class RectangularModel(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.pos = None
        self.startPoint=QPointF()
        self.lastPoint=QPointF()
        self.currentPoint=QPointF()
        self.pen=QPen(Qt.black)
        self.brush=QBrush(Qt.Dense6Pattern)
        self._dragMode = False
        self._changeSelection=False
        self.startPoint.x=-1
        self.startPoint.y=-1
        self.scene = QGraphicsScene()


    def beginSelecting(self, pos):
        self._dragMode = True
        self.scene.clear()
        if self.startPoint.x == -1 and self.startPoint.y == -1:
            self.startPoint.x, self.startPoint.y= pos[0], pos[1]
            self._changeSelection=True
    
    
    def drawRectangle(self, p1, p2):
        self.rect = QRect()
        if p1.x < p2.x:
            self.rect.x = p1.x
            self.rect.width = p2.x-p1.x
        else:
            self.rect.x = p2.x
            self.rect.width = p1.x-p2.x
        if p1.y < p2.y:
            self.rect.y = p1.y
            self.rect.height = p2.y-p1.y
        else:
            self.rect.y = p2.y
            self.rect.height = p1.y-p2.y
        #TODO paint rectangle
        tempi = QImage(QSize(self.rect.width, self.rect.height), QImage.Format_ARGB32_Premultiplied)
        painter=QPainter(tempi)
        print "painter active ?", painter.isActive()
        painter.drawRect(self.rect.x,self.rect.y,self.rect.width,self.rect.height)
        painter.end()
        self.scene.addRect(self.rect.x, self.rect.y, self.rect.width, self.rect.height, self.pen, self.brush )
        
    def moveTo(self,pos):
        if self._dragMode == True:
            if self._changeSelection is True:
                if pos[0 ]== self.lastPoint.x and pos[1] > self.startPoint.y and pos[1] < self.lastPoint.y:
                    self.currentPoint.x = pos[0]
                    self.currentPoint.y = self.lastPoint.y
                    self.drawRectangle(self.startPoint, self.currentPoint)
                elif pos[0] == self.startPoint.x and pos[1] > self.startPoint.y and pos[1] < self.lastPoint.y:
                    self.currentPoint.x = self.lastPoint.x
                    self.currentPoint.y = self.lastPoint.y
                    self.startPoint.x = pos[0]
                    self.drawRectangle(self.startPoint, self.currentPoint)
                elif pos[0]== self.startPoint.y and pos[1] > self.startPoint.x and pos[1] < self.lastPoint.x:
                    self.currentPoint.x = self.lastPoint.x
                    self.currentPoint.y = self.lastPoint.y
                    self.startPoint.y = pos[1]
                    self.drawRectangle(self.startPoint, self.currentPoint)
                elif pos[0] == self.lastPoint.y and pos[1] > self.startPoint.x and pos[1] < self.lastPoint.x:
                    self.currentPoint.x = self.lastPoint.x
                    self.currentPoint.y = pos[1]
                    self.drawRectangle(self.startPoint, self.currentPoint)
                else:
                    self.endSelecting(pos)
            else:
                self.currentPoint.x, self.currentPoint.y = pos[0], pos[1]
                self.drawRectangle(self.startPoint, self.currentPoint)
                
    def endSelecting(self, pos):
        self._dragMode = False
        self.lastPoint.x, self.lastPoint.y = pos[0], pos[1]
        self.drawRectangle(self.startPoint,self.lastPoint)
        
    def dumpSelecting(self, pos):
        self.startPoint.x=-1
        self.startPoint.y=-1
        self._changeSelection=False
        
        
    

    