from PyQt4.QtCore import QAbstractListModel, pyqtSignal, QModelIndex, Qt, \
                         QTimer
from PyQt4.QtGui import QItemSelectionModel

from layer import Layer

#*******************************************************************************
# L a y e r S t a c k M o d e l                                                *
#*******************************************************************************

class LayerStackModel(QAbstractListModel):
    canMoveSelectedUp = pyqtSignal("bool")
    canMoveSelectedDown = pyqtSignal("bool")
    canDeleteSelected = pyqtSignal("bool")
    
    orderChanged = pyqtSignal()
        
    def __init__(self, parent = None):
        QAbstractListModel.__init__(self, parent)
        self._layerStack = []
        self.selectionModel = QItemSelectionModel(self)
        self.selectionModel.selectionChanged.connect(self.onSelectionChanged)
        QTimer.singleShot(0, self.updateGUI)
        
    def __repr__(self):
        return "<LayerStackModel: layerStack='%r'>" % (self._layerStack,)  
    
    def __getitem__(self, i):
        return self._layerStack[-i-1]
    
    def __iter__(self):
        return reversed(self._layerStack)
        
    def updateGUI(self):
        self.canMoveSelectedUp.emit(self.selectedRow()>0)
        self.canMoveSelectedDown.emit(self.selectedRow()<self.rowCount()-1)
        self.canDeleteSelected.emit(self.rowCount() > 0)
        self.wantsUpdate()
    
    def append(self, data):
        #self.insertRow(self.rowCount())
        #self.setData(self.index(self.rowCount()-1), data)
        self.insertRow(0)
        self.setData(self.index(0), data)
    
    def selectedRow(self):
        selected = self.selectionModel.selectedRows()
        if len(selected) == 1:
            return selected[0].row()
        return -1
    
    def selectedIndex(self):
        row = self.selectedRow()
        if row >= 0:
            return self.index(self.selectedRow())
        else:
            return QModelIndex()
    
    def onSelectionChanged(self, selected, deselected):
        if len(deselected) > 0:
            self._layerStack[deselected[0].indexes()[0].row()].mode = 'ReadOnly'
        if len(selected) > 0:
            self._layerStack[selected[0].indexes()[0].row()].mode = 'Expanded'
        self.updateGUI()
    
    def rowCount(self, parent = QModelIndex()):
        if not parent.isValid():
            return len(self._layerStack)
        return 0
    
    def insertRows(self, row, count, parent = QModelIndex()):
        if parent.isValid():
            return False
        oldRowCount = self.rowCount()
        beginRow = max(0,row)
        endRow   = min(row+count-1, len(self._layerStack))
        self.beginInsertRows(parent, beginRow, endRow) 
        while(beginRow <= endRow):
            self._layerStack.insert(row, Layer())
            beginRow += 1
        self.endInsertRows()
        assert self.rowCount() == oldRowCount+1
        return True
            
    def removeRows(self, row, count, parent = QModelIndex()):
        if parent.isValid():
            return False
        if row+count <= 0 or row >= len(self._layerStack):
            return False
        oldRowCount = self.rowCount()
        beginRow = max(0,row)
        endRow   = min(row+count-1, len(self._layerStack)-1)
        self.beginRemoveRows(parent, beginRow, endRow)
        while(beginRow <= endRow):
            del self._layerStack[row]
            beginRow += 1
        
        self.endRemoveRows()
        assert self.rowCount() == oldRowCount-1
        return True
    
    def flags(self, index):
        defaultFlags = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        if index.isValid():
            return Qt.ItemIsDragEnabled | defaultFlags
        else:
            return Qt.ItemIsDropEnabled | defaultFlags
    
    def supportedDropActions(self):
        return Qt.MoveAction
    
    def data(self, index, role):
        if not index.isValid():
            return None
        if index.row() > len(self._layerStack):
            return None
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._layerStack[index.row()]
        
        return None
    
    def setData(self, index, value, role = Qt.EditRole):
        layer = value
        if not isinstance(value, Layer):
            layer = value.toPyObject()
        self._layerStack[index.row()] = layer
        self.dataChanged.emit(index, index)
        return True
    
    def headerData(section, orientation, role = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return QString("Column %1").arg(section)
        else:
            return QString("Row %1").arg(section)
        
    def wantsUpdate(self):
        self.layoutChanged.emit()

    def deleteSelected(self):
        print "delete"
        assert len(self.selectionModel.selectedRows()) == 1
        row = self.selectionModel.selectedRows()[0]
        self.removeRow(row.row())
        if self.rowCount() > 0:
            self.selectionModel.select(self.index(0), QItemSelectionModel.Select)
        self.updateGUI()

    def moveSelectedUp(self):
        assert len(self.selectionModel.selectedRows()) == 1
        row = self.selectionModel.selectedRows()[0]
        if row.row() != 0:
            oldRow = row.row()
            newRow = oldRow - 1
            d = self._layerStack[oldRow]
            self.removeRow(oldRow)
            self.insertRow(newRow)
            self.setData(self.index(newRow), d)
            self.selectionModel.select(self.index(newRow), QItemSelectionModel.Select)
            self.orderChanged.emit()
            self.updateGUI()
    
    def moveSelectedDown(self):
        assert len(self.selectionModel.selectedRows()) == 1
        row = self.selectionModel.selectedRows()[0]
        if row.row() != self.rowCount() - 1:
            oldRow = row.row()
            newRow = oldRow + 1
            d = self._layerStack[oldRow]
            self.removeRow(oldRow)
            self.insertRow(newRow)
            self.setData(self.index(newRow), d)
            self.selectionModel.select(self.index(newRow), QItemSelectionModel.Select)
            self.orderChanged.emit()
            self.updateGUI()
