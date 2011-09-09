# -*- coding: utf-8 -*-



from PyQt4.QtCore import pyqtSignal, QObject, QRectF
from PyQt4.QtGui import QGraphicsRectItem, QGraphicsScene

                     
class RectangularModel(QObject):
    currentRectangleChanged = pyqtSignal(int, int, int, int)
    
    def __init__(self):
        QObject.__init__(self)
        self.sliceRect = None
        self.pos = None
        self.startPoint = (-1,-1)
        self.lastPoint=None
        self.rect = QRectF()
        self.firstSelection = True
        self.selectedRect = []
        self.currentRect = QRectF()
        self.isSelecting = False

    def beginSelecting(self, pos):
        self.isSelecting = True 
        if self.startPoint == (-1,-1):
            self.startPoint = (pos[0]+0.0001, pos[1]+0.0001)
            self.currentRect = QRectF(self.startPoint[0], self.startPoint[1], 0, 0)
            self.moveTo(pos)
        
        elif self.rect.x - 5 < pos[0] < self.rect.x + 5 or self.rect.y - 5 < pos[1] < self.rect.y + 5 or (self.rect.x + self.rect.width) - 5 < pos[0] < (self.rect.x + self.rect.width) + 5 or (self.rect.y + self.rect.height) - 5 < pos[1] < (self.rect.y + self.rect.height) + 5: 
            self.lastPoint = (self.rect.x + self.rect.width, self.rect.y + self.rect.height)
            ## select the bottom-right corner of the rectangle
            if self.lastPoint[0]-12 < pos[0] < self.lastPoint[0] + 12 and self.rect.y -12< pos[1] <self.rect.y + 12:
                self.startPoint = (self.rect.x, self.rect.y + self.rect.height)
                self.moveTo(pos)
        
            ## select the top-right corner of the rectangle
            if self.lastPoint[0] -12 < pos[0] < self.lastPoint[0] + 12 and self.lastPoint[1] -12< pos[1] <self.lastPoint[1] + 12:
                self.startPoint = (self.rect.x, self.rect.y)
                self.moveTo(pos)
        
            ## select the top-left corner of the rectangle
            if self.rect.x -12 < pos[0] < self.rect.x + 12 and self.lastPoint[1] -12< pos[1] <self.lastPoint[1] + 12:
                self.startPoint = (self.lastPoint[0], self.rect.y)
                self.moveTo(pos)
        
            ## select the bottom-left corner of the rectangle
            if self.rect.x -12 < pos[0] < self.rect.x + 12 and self.rect.y -12< pos[1] <self.rect.y + 12:
                self.startPoint = (self.lastPoint[0], self.lastPoint[1])
                self.moveTo(pos)
        else:
            self.startPoint = (pos[0]+0.0001, pos[1]+0.0001)
            self.currentRect = QRectF(pos[0]+0.0001, pos[1]+0.0001, 0,0)
            self.currentRectangleChanged.emit(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
            self.moveTo(pos)

    def moveTo(self,pos):
        if not self.isSelecting:
            return
        #draw rectangle
        if self.startPoint[0] < pos[0]:
            self.rect.x = self.startPoint[0]
            self.rect.width = pos[0]-self.startPoint[0]
        else:
            self.rect.x = pos[0]
            self.rect.width = self.startPoint[0]-pos[0]
        if self.startPoint[1] < pos[1]:
            self.rect.y = self.startPoint[1]
            self.rect.height = pos[1]-self.startPoint[1]
        else:
            self.rect.y = pos[1]
            self.rect.height = self.startPoint[1]-pos[1]
        self.currentRect = QRectF(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.currentRectangleChanged.emit(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

    def endSelecting(self, pos):
        if not self.isSelecting:
            return
        self.isSelecting = False
        self.currentRect = QRectF(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        #self.currentRectangleChanged.emit(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        #self.moveTo(pos)


        