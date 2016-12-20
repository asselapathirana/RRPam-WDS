from epanettools.epanettools import Link
from epanettools.epanettools import Node
from PyQt5.QtWidgets import QTableView, QDialog, QVBoxLayout
from PyQt5.QtCore import Qt


import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt


def table_editor(parent, arr):
    #if editor.setup_and_check(self.arr, title=label):
    numpymodel=NumpyModel(arr)
    editor = QTableView()
    editor.setModel(numpymodel)
    dialog = QDialog(parent=parent)
    layout = QVBoxLayout()
    layout.addWidget(editor)
    dialog.setLayout(layout)
    dialog.setAttribute(Qt.WA_DeleteOnClose)
    ret=dialog.exec_()
    return ret

# see http://stackoverflow.com/questions/11736560/edit-table-in-pyqt-using-qabstracttablemodel
# and http://doc.qt.io/qt-4.8/model-view-programming.html#making-the-model-editable
class NumpyModel(QtCore.QAbstractTableModel):
    def __init__(self, narray, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._array = narray

    def rowCount(self, parent=None):
        return self._array.shape[0]

    def columnCount(self, parent=None):
        return self._array.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if (role == Qt.DisplayRole or  role == Qt.EditRole):
                row = index.row()
                col = index.column()
                try:
                    1+self._array[row, col]
                    return QtCore.QVariant("%.5f"%self._array[row, col])
                except TypeError:                
                    return QtCore.QVariant("%s"%self._array[row, col])

        return QtCore.QVariant()
    
    def setData(self, index, value, role):
        if (index.isValid() and role==Qt.EditRole):
            self._array[index.row()][index.column()] = value
            #emit dataChanged(index, index);
            return True
    
    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable 


def get_title(epanet_network_item):
    return _get_type(epanet_network_item)[0]


def get_icon(epanet_network_item):
    return _get_type(epanet_network_item)[1]


def _get_type(epanet_network_item):
    if isinstance(epanet_network_item, Node):
        return "N:" + epanet_network_item.id, 'node.png'
    if isinstance(epanet_network_item, Link):
        return "L:" + epanet_network_item.id, 'link.png'
    if isinstance(epanet_network_item, str):
        if(epanet_network_item == "Risk"):
            return "R:", 'link.png'

    return "None", "curve.png"
