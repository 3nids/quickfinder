
from PyQt4.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt4.QtGui import QErrorMessage

from qgis.core import QgsProject, QgsMapLayerRegistry, QgsVectorLayer

from quickfinder.core.ftsconnection import FtsConnection

from quickfinder.core.mysettings import MySettings


class Search():
    def __init__(self, searchName, layerid, layerName, expression, priority, dateEvaluated=None):
        self.searchName = searchName
        self.layerid = layerid
        self.layerName = layerName
        self.expression = expression
        self.priority = priority
        self.dateEvaluated = dateEvaluated

        self.status = 'evaluated'
        self.layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not self.layer:
            self.status = "layer_deleted"
        elif dateEvaluated:
            self.status = "not_evaluated"



class LocalSearchModel(QAbstractItemModel):

    # default invalid connection
    fts = FtsConnection()

    # list( list( layer / expression / priority / status / date_evaluated ) )
    searches = list()

    def __init__(self):
        QAbstractItemModel.__init__(self)

    def setFtsConnection(self, ftsConnection):
        self.fts = ftsConnection

    # def readFromFile(self, filepath):
    #     self.beginResetModel()
    #     searches = list()
    #     if not self.fts.isValid:
    #         return
    #     self.endResetModel()


    def addSearch(self, searchName, layerid, layerName, expression, priority, evaluateDirectly):
        if evaluateDirectly:
            ok, message = self.fts.evaluateSearch(searchName, layerid, expression, priority)
            if not ok:
                QErrorMessage().showMessage(message)
        else:
            self.beginInsertRows(QModelIndex(), 0, 1)
            search = Search(searchName, layerid, layerName, expression, priority)
            self.searches.insert(0, search)
            self.endInsertRows()


    def index(self, row, column, parent=QModelIndex()):
        if row < 0 or row >= self.rowCount():
            return QModelIndex()
        return self.createIndex( row, column, row )

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self.searches)

    def columnCount(self, parent=QModelIndex()):
        return 4

    def headerData(self, section, Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if section == 0:
                return 'Name'
            elif section == 1:
                return 'Layer'
            elif section == 2:
                return 'Expression'
            elif section == 3:
                return 'Evaluated on'

        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self.searches):
            return None

        search = self.searches[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return search.searchName
            elif col == 1:
                return search.layerName
            elif col == 2:
                return search.expression
            elif col == 3:
                return search.dateEvaluated
            
        if role == Qt.UserRole and col == 0:
            return search.layerid

        return None














