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
            print "on mouse Move"
            self._rectangularModel.moveTo(pos)

    def onLeftMouseButtonPress(self,pos, shape):
        print "on left Mouse Button Pressed"
        self._buttonDown = True
        self._rectangularModel.beginSelecting(pos)       
        
    def onMouseButtonRelease(self,pos):
        print "on Mouse Button Release"
        self._rectangularModel.endSelecting(pos)
        self._buttonDown = False
        
    def onWheel(self,delta,axis):
        print "rectangular selection is enabled"

    def onMouseButtonDblClick(self,x,y,axis):
        print "rectangular selection is enabled"
        
# RECTANGULAR CONTROLER


class RectangularControler(QObject):
    def __init__(self, imageViews, rectangularModel):
        QObject.__init__(self, parent=None)
        self._rectangularModel = rectangularModel
        self._imageViews = imageViews
        #slice = self._imageViews2Ds.slice
        #rectItem = QGraphicsRectItem()
        self.pen=QPen(Qt.black)
        self.brush=QBrush(Qt.Dense6Pattern)
        self.scene_data=[]
        #self.rectangularModel.selectedRectangle.connect(self.paintEvent)
        self._rectangularModel.argsChanged.connect(self._currentSelectedRectangleList)
        

        def _currentSelectedRectangleList(self, watched):
            imageView = watched.parent()
            for i in range(3):
                view = self._imageViews[i]
                if view == imageView:
                    break
            view = imageView
            #view.scene.addRect(self._rectangularModel.rect.x, self._rectangularModel.rect.y, self._rectangularModel.rect.width, self._rectangularModel.rect.height, self.pen, self.brush)
            self.scene_data.append({'routine':view.scene.addRect,'args':(self._rectangularModel.rect.x, self._rectangularModel.rect.y, self._rectangularModel.rect.width, self._rectangularModel.rect.height, self.pen, self.brush)})
            #view.scene.clear()
        def draw_next_item(self):
            d = self.scene_data.pop(len(self.scene_data)-1) # get last item
            item = d['routine'](*d['args'])
            #item.show()
            #rPainter.drawItem()
            
        '''
        
        def paintEvent(self):
            rPainter = QPainter()
            rPainter.begin(self)
        
            self._draw_next_item(rPainter)
        
            rPainter.end()
            
        '''
