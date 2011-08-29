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
        self.currentPoint=None
        #self.pen=QPen(Qt.black)
        #self.brush=QBrush(Qt.Dense6Pattern)
        self._dragMode = False
        self.rect = QRectF()



    def beginSelecting(self, pos):
        if self.startPoint == (-1,-1):
            self.startPoint = (pos[0]+0.0001, pos[1]+0.0001)
            self._dragMode = True
            self.moveTo(pos)
            

    
    def drawRectangle(self, p1, p2):
        if p1[0] < p2[0]:
            self.rect.x = p1[0]
            self.rect.width = p2[0]-p1[0]
        else:
            self.rect.x = p2[0]
            self.rect.width = p1[0]-p2[0]
        if p1[1] < p2[1]:
            self.rect.y = p1[1]
            self.rect.height = p2[1]-p1[1]
        else:
            self.rect.y = p2[1]
            self.rect.height = p1[1]-p2[1]
        print 'rect.x =',  self.rect.x
        print 'rect.y =', self.rect.y
        print 'rect.width =', self.rect.width
        print 'rect.height =', self.rect.height
        #self.scene.addRect(self.rect.x, self.rect.y, self.rect.width, self.rect.height, self.pen, self.brush )
        self.argsChanged.emit(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

    def moveTo(self,pos):
        if self._dragMode:
            self.currentPoint= (pos[0], pos[1])
            print 'current Point =', self.currentPoint[0], self.currentPoint[1]
            print 'start point = ' , self.startPoint[0], self.startPoint[1]
            self.drawRectangle(self.startPoint, self.currentPoint)

        else:
            self.currentPoint= (pos[0], pos[1])
            print 'current Point =' , self.currentPoint[0], self.currentPoint[1]
            print 'start point = ' , self.startPoint[0], self.startPoint[1]
            self.drawRectangle(self.startPoint, self.currentPoint)
            #self.selectedRectangle.emit(self.startPoint,self.currentPoint)
            
    def endSelecting(self, pos):
        self._dragMode = False
        self.moveTo(pos)

        
    def dumpSelecting(self, pos):
        self.startPoint = (-1,-1)
        self._changeSelection=False

    

    