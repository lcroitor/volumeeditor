# -*- coding: utf-8 -*-


from PyQt4.QtCore import QObject, QThread, Qt, QPointF, QRectF, \
                         QRect, QPoint, QSizeF
from PyQt4.QtGui  import QWidget, QPen, QBrush, QColor,\
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
        self.startPoint.x=-1
        self.startPoint.y=-1


    def beginSelecting(self, pos):
        self._dragMode = True
        if self.startPoint.x == -1 and self.startPoint.y == -1:
            self.startPoint.x, self.startPoint.y= pos[0], pos[1]
    
    
    def drawRectangle(self, p1, p2):
        self.rect = QRectF()
        if p1.x < p2.x:
            self.rect.x = p1.x
            self.rect.width = p2.x-p1.x
            print "rect.width", self.rect.width
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
        painter=QPainter()
        print "painter active ?", painter.isActive()
        painter.drawRect(self.rect.x,self.rect.y,self.rect.width,self.rect.height)
        fill=self.brush
        painter.fillRect(self.rect,fill)

    def moveTo(self,pos):
        if self._dragMode == True:
            self.currentPoint.x, self.currentPoint.y = pos[0], pos[1]
            self.drawRectangle(self.startPoint, self.currentPoint)
            

    def endSelecting(self, pos):
        self._dragMode = False
        self.lastPoint.x, self.lastPoint.y = pos[0], pos[1]
        self.drawRectangle(self.startPoint,self.lastPoint)
        
    def dumpSelecting(self, pos):
        self.startPoint.x=-1
        self.startPoint.y=-1
        
        
    

    