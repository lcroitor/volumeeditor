# -*- coding: utf-8 -*-


from PyQt4.QtCore import pyqtSignal, QObject, QRectF
                        
                         
                         
class RectangularModel(QObject):

    #selectedRectangle = pyqtSignal(QPointF,QPointF)
    argsChanged = pyqtSignal(int, int, int, int)
    
    def __init__(self):
        QObject.__init__(self)
        self.pos = None
        self.startPoint=(-1,-1)
        self.lastPoint=None
        self._selectedCorner = False
        self.rect = QRectF()



    def beginSelecting(self, pos):
        if self.startPoint == (-1,-1):
            self.startPoint = (pos[0]+0.0001, pos[1]+0.0001)
            self.moveTo(pos)
        else:
            self.lastPoint = (self.rect.x + self.rect.width, self.rect.y + self.rect.height)
            ## select the bottom-right corner of the rectangle
            if self.lastPoint[0]-12 < pos[0] < self.lastPoint[0] + 12 and self.rect.y -12< pos[1] <self.rect.y + 12:
                self.startPoint[0] = self.rect.x
                self.startPoint[1] = self.rect.y + self.rect.height    
                self._selectedCorner = True
                self.moveTo(pos)
            ## select the top-right corner of the rectangle
            if self.lastPoint[0] -12 < pos[0] < self.lastPoint[0] + 12 and self.lastPoint[1] -12< pos[1] <self.lastPoint[1] + 12:
                self.startPoint = (self.rect.x, self.rect.y)    
                self._selectedCorner = True
                self.moveTo(pos)
            ## select the top-left corner of the rectangle
            if self.rect.x -12 < pos[0] < self.rect.x + 12 and self.lastPoint[1] -12< pos[1] <self.lastPoint[1] + 12:
                self.startPoint = (self.lastPoint[0], self.rect.y)  
                self._selectedCorner = True
                self.moveTo(pos)
            ## select the bottom-left corner of the rectangle
            if self.rect.x -12 < pos[0] < self.rect.x + 12 and self.rect.y -12< pos[1] <self.rect.y + 12:
                self.startPoint = (self.lastPoint[0], self.lastPoint[1])   
                self._selectedCorner = True
                self.moveTo(pos)
            

    def moveTo(self,pos):
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
        print 'rect.x =',  self.rect.x, self.rect.y, self.rect.width, self.rect.height
        #self.resize(pos[0],pos[1],self.rect.width, self.rect.height)
        self.argsChanged.emit(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    ''' 
    def resize(self,x,y,width,height):
        newRect=QRectF()
        newRect.x = x
        newRect.y = y
        newRect.width=width
        newRect.height=height
        print 'newRect', newRect.x, newRect.y, newRect.width, newRect.height
        if newRect == self.rect:
            self.argsChanged.emit(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        else:
            self.rect=newRect
            self.argsChanged.emit(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    '''
         
            
    def endSelecting(self, pos):
        if self._selectedCorner is True:
            self.moveTo(pos)
        
    def dumpSelecting(self, pos):
        self.startPoint = (-1,-1)
        self._selectedCorner = False
        
