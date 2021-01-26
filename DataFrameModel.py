from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pandas as pd

class DataFrameModel(QtCore.QAbstractTableModel):

    def __init__(self, data, standards=None):
        QtCore.QAbstractTableModel.__init__(self)
        data.index.name = ''
        data.reset_index(inplace=True)
        self._data = data
        self.standards = standards

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                try:
                    return str(self._data.iloc[index.row(), index.column()])#'{:.4e}'.format(self._data.iloc[index.row(), index.column()])
                except:
                    return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.FontRole and self._data[''][index.row()] == '':
                font = QFont()
                font.setBold(True)
                return font
            if role == Qt.TextAlignmentRole and self._data[''][index.row()] == '':
                return Qt.AlignCenter
            if role == Qt.BackgroundRole:
                if self.standards is not None:
                    if self._data[''][index.row()] == '':
                        return QtGui.QBrush(Qt.white)
                    elif self.standards in self._data[''][index.row()]:
                        return QtGui.QBrush(QtGui.QColor(200, 255, 220))
                    else:
                        return QtGui.QBrush(QtGui.QColor(220, 220, 220))
                return QtGui.QBrush(Qt.white)

        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._data.columns[col]
            if role == Qt.FontRole:
                font = QFont()
                font.setBold(True)
                return font
        return None


'''class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles'''