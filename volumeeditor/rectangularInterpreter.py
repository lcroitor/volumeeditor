# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject, QRectF
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
        print 'calling begin selecting with pos=%r' % (pos,)
        self._rectangularModel.beginSelecting(pos)       
        
    def onMouseButtonRelease(self,pos):
        self._rectangularModel.endSelecting(pos)
        self._buttonDown = False
        
    def onWheel(self,delta,axis):
        print "rectangular selection is enabled"

    def onMouseButtonDblClick(self,x,y,axis):
        print "rectangular selection is enabled"
        
# RECTANGULAR CONTROLER


class RectangularControler(QObject):
    def __init__(self, rectangularModel,positionModel, imageViews):
        QObject.__init__(self, parent=None)
        self._rectangularModel = rectangularModel
        self._positionModel = positionModel
        self._imageViews = imageViews
        #slice = self._imageViews2Ds.slice
        #rectItem = QGraphicsRectItem()
        self.pen=QPen(Qt.black)
        self.brush=QBrush(Qt.Dense6Pattern)
        self.sceneData=[]
        

    def selectedRectList(self):
        view = self._positionModel.activeView
        print 'view ist', view 
        activeView = self._imageViews[view]
        print 'active view', activeView
        print 'self.rect.x, self.rect.y, self.rect.width, self.rect.height', self._rectangularModel.rect.x, self._rectangularModel.rect.y, self._rectangularModel.rect.width, self._rectangularModel.rect.height, self.pen, self.brush
        
            #view.scene.addRect(self._rectangularModel.rect.x, self._rectangularModel.rect.y, self._rectangularModel.rect.width, self._rectangularModel.rect.height, self.pen, self.brush)
        self.sceneData.append({'routine':activeView.scene().addRect,'args':(self._rectangularModel.rect.x, self._rectangularModel.rect.y, self._rectangularModel.rect.width, self._rectangularModel.rect.height, self.pen, self.brush)})
            #view.scene.clear()
        print 'list =', self.sceneData
        self.draw_next_item()
    def draw_next_item(self):
            d = self.sceneData.pop(len(self.sceneData)-1) # get last item
            item = d['routine'](*d['args'])
            print 'item is', item
            #item.show()
            #rPainter.drawItem()
            
    '''
        
    def paintEvent(self):
        rPainter = QPainter()
        rPainter.begin(self)
        
        self._draw_next_item(rPainter)
        
        rPainter.end()
            
        '''
