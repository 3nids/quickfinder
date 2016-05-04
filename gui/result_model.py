#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2014 Denis Rouzaud, Arnaud Morvan
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


from PyQt4.QtCore import Qt
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon


class BaseItem(QStandardItem):
    def __init__(self, name):
        super(BaseItem, self).__init__(name)
        self.name = name
        self.setSelectable(False)


class GroupItem(BaseItem):

    def __init__(self, name):
        super(GroupItem, self).__init__(name)
        self.count = 0

        font = self.font()
        font.setWeight(QFont.Bold)
        self.setFont(font)

    def setName(self, name):
        self.name = name
        self.emitDataChanged()

    def increment(self):
        self.count += 1
        self.emitDataChanged()

    def data(self, role):
        if role == Qt.DisplayRole:
            return u'{0} ({1})'.format(self.name, self.count)
        else:
            return super(GroupItem, self).data(role)


class CategoryItem(GroupItem):
    def __init__(self, name):
        super(CategoryItem, self).__init__(name)

class LayerItem(GroupItem):
   def __init__(self, name):
        super(LayerItem, self).__init__(name)


class ResultItem(BaseItem):
    def __init__(self, name):
        super(ResultItem, self).__init__(name)
        self.geometry = None


class ResultModel(QStandardItemModel):
    def __init__(self, parent):
        super(ResultModel, self).__init__(parent)
        # keep items references on python side
        # http://www.riverbankcomputing.com/pipermail/pyqt/2013-March/032417.html
        # http://www.riverbankcomputing.com/pipermail/pyqt/2013-April/032712.html
        self.items = []
        self.selected = None

    def setLoading(self, isLoading):
        root = self.invisibleRootItem()
        item = root.child(0)
        if item is None:
            return
        if isLoading:
            icon = QIcon(":/plugins/quickfinder/icons/loading.gif")
        else:
            icon = QIcon()
        item.setIcon(icon)

    def truncateHistory(self, limit):
        root = self.invisibleRootItem()
        for i in xrange(root.rowCount() - 1, limit - 1, -1):
            item = root.child(i)
            if not isinstance(item, CategoryItem):
                root.removeRow(item.row())

    def clearResults(self):
        root = self.invisibleRootItem()
        for i in xrange(root.rowCount() - 1, -1, -1):
            item = root.child(i)
            if isinstance(item, CategoryItem):
                root.removeRow(item.row())
        self.selected = None
        self.items = []

    def _childItem(self, parent, name, createclass=None):
        for i in xrange(0, parent.rowCount()):
            child = parent.child(i)
            if isinstance(child, createclass) and child.name == name:
                return child

        if createclass:
            child = createclass(name)
            self.items.append(child)
            parent.appendRow(child)
            return child

    def addResult(self, category, layer='', value='', geometry=None, srid=None):
        root_item = self.invisibleRootItem()

        category_item = self._childItem(root_item, category, CategoryItem)

        if layer == '':
            return
        layer_item = self._childItem(category_item, layer, LayerItem)

        if value == '':
            return
        category_item.increment()
        layer_item.increment()

        item = ResultItem(value)
        item.geometry = geometry
        item.srid = srid
        layer_item.appendRow(item)

    def setSelected(self, item, palette):
        if self.selected:
            self.selected.setData(self.selected.initialBackgroundColor, Qt.BackgroundColorRole)
            self.selected.setData(self.selected.initialForegroundColor, Qt.ForegroundRole)

        if item:
            item.initialBackgroundColor = item.data(Qt.BackgroundColorRole)
            item.initialForegroundColor = item.data(Qt.ForegroundRole)
            item.setData(palette.highlight(), Qt.BackgroundColorRole)
            item.setData(palette.highlightedText(), Qt.ForegroundRole)

        self.selected = item
