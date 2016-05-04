# -----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2013 Denis Rouzaud
#
# -----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ---------------------------------------------------------------------

from uuid import uuid1
from PyQt4.QtCore import Qt, QAbstractItemModel, QModelIndex
from ..core.project_search import ProjectSearch

LayerIdRole = Qt.UserRole + 1
SearchIdRole = Qt.UserRole + 2

class ProjectSearchModel(QAbstractItemModel):

    searches = {}

    def __init__(self, project_finder):
        QAbstractItemModel.__init__(self)
        self.project_finder = project_finder
        self.project_finder.fileChanged.connect(self.fileChanged)

    def fileChanged(self):
        self.beginResetModel()
        self.searches = self.project_finder.searches
        for search in self.searches.values():
            search.changed.connect(self.searchChanged)
        self.endResetModel()

    def addSearch(self, searchName, layer, expression, priority):
        searchId = unicode(uuid1())
        srid = layer.crs().authid()
        projectSearch = ProjectSearch(searchId, searchName, layer.id(), layer.name(), expression, priority, srid)
        self.beginInsertRows(QModelIndex(), 0, 0)
        self.searches[searchId] = projectSearch
        self.searches[searchId].changed.connect(self.searchChanged)
        self.endInsertRows()
        return self.searches[searchId]

    def removeSearches(self, searchIds):
        self.beginResetModel()
        for searchId in searchIds:
            self.project_finder.deleteSearch(searchId)
            del self.searches[searchId]
        self.endResetModel()

    def searchChanged(self):
        self.modelReset.emit()

    def index(self, row, column, parent=QModelIndex()):
        if row < 0 or row >= self.rowCount():
            return QModelIndex()
        return self.createIndex(row, column, row)

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self.searches)

    def columnCount(self, parent=QModelIndex()):
        return 5

    def headerData(self, section, Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if section == 0:
                return 'Name'
            elif section == 1:
                return 'Layer'
            elif section == 2:
                return 'Expression'
            elif section == 3:
                return 'Priority'
            elif section == 4:
                return 'Evaluated on'
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self.searches):
            return None

        search = self.searches.values()[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return search.searchName
            elif col == 1:
                return search.layerName
            elif col == 2:
                return search.expression
            elif col == 3:
                return search.priority
            elif col == 4:
                return search.dateEvaluated

        if role == LayerIdRole:
            return search.layerid

        if role == SearchIdRole:
            return search.searchId

        if role == Qt.TextAlignmentRole:
            if col == 3:
                return Qt.AlignVCenter + Qt.AlignRight

        return None
