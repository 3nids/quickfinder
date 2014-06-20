#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2013 Denis Rouzaud
#
#-----------------------------------------------------------
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
#---------------------------------------------------------------------

from PyQt4.QtCore import Qt, QAbstractItemModel, QModelIndex


class LocalSearchModel(QAbstractItemModel):

    searches = list()

    def __init__(self):
        QAbstractItemModel.__init__(self)

    def setSearches(self, searches):
        self.beginResetModel()
        self.searches = searches
        self.endResetModel()

    def addSearch(self, localSearch):
        self.beginInsertRows(QModelIndex(), 0, 0)
        self.searches.insert(0, localSearch)
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














