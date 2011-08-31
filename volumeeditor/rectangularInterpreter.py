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
        self.pen=QPen(Qt.black)
        self.brush=QBrush(Qt.Dense6Pattern)
        self.sceneData=[]
        self.initialPos=None
        
    def selectedRectList(self):

        view = self._positionModel.activeView
        activeView = self._imageViews[view]
        self.initialPos = (self._rectangularModel.rect.x,self._rectangularModel.rect.y)
        #self.initialPos=(x,y)
        print 'initial pos is', self.initialPos
        #self.mapPos = activeView.mapScene2Data(activeView.mapToScene(self.initialPos[0],self.initialPos[1]))
        #self.mapPos = activeView.mapToScene(self.initialPos[0],self.initialPos[1])
        
        #self.mapPos = activeView.mapToScene(self.initialPos[0],self.initialPos[1])
        #x = self.mapPos.x()
        #y = self.mapPos.y()
        
        from PyQt4.QtCore import QPointF
        mapPos = activeView.scene().scene2data.map(QPointF(self.initialPos[0],self.initialPos[1] ))
        x,y = mapPos.x(), mapPos.y()
        
        #mapRect = activeView.scene().scene2data.mapRect(self._rectangularModel.rect)
        #self._rectangularModel.resize(x,y,width,height)
        
        #wrong
        width = self._rectangularModel.rect.height
        height = self._rectangularModel.rect.width
        
        self.sceneData.append({'routine':activeView.scene().addRect,'args':(x, y, width, height, self.pen, self.brush)})
        activeView.scene().clear()
        #print 'list =', self.sceneData
        self.draw_next_item()
    def draw_next_item(self):
        d = self.sceneData.pop(len(self.sceneData)-1) # get last item
        #item = self.sceneData.pop(len(self.sceneData)-1)
        item = d['routine'](*d['args'])
        print 'item is', item
        item.show()        

        
        