'''
Created on 25 mars 2014

@author: arnaud
'''

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QFont

class ResultModel(QStandardItemModel):

    categories = {}

    textRole = Qt.UserRole + 1
    countRole = Qt.UserRole + 2
    geometryRole = Qt.UserRole + 3

    def clearResults(self):
        root = self.invisibleRootItem()
        for category in self.categories.values():
            root.removeRow(category.row())
        self.categories.clear()

    def _childItem(self, parent, text, create=False, increment=False, group=False):
        item = None
        for i in xrange(0, parent.rowCount()):
            child = parent.child(i)
            if child.data(self.textRole) == text:
                item = child
                break

        if create and not item:
            child = QStandardItem(text)
            child.setData(text, self.textRole)
            if group:
                font = child.font()
                font.setWeight(QFont.Bold)
                child.setFont(font)
                child.setSelectable(False)
            child.setData(0, self.countRole)
            parent.appendRow(child)

        if increment:
            count = int(child.data(self.countRole)) + 1
            child.setData(count, self.countRole)
            text = child.data(self.textRole)
            display = '{0} ({1})'.format(text, count)
            child.setText(display)

        return child

    def _categoryItem(self, category, create=False, increment=False):
        root = self.invisibleRootItem()
        item = self._childItem(root, category, create, increment, True)
        self.categories[category] = item
        return item

    def _layerItem(self, category, layer, create=False, increment=False):
        parent = self._categoryItem(category, create, increment)
        item = self._childItem(parent, layer, create, increment, True)
        return item

    def _valueItem(self, category, layer, value, geometry, create=False, increment=False):
        parent = self._layerItem(category, layer, create, increment)
        item = self._childItem(parent, value, create)
        item.setData(geometry, self.geometryRole)
        return item

    def addResult(self, category, layer, value, geometry):
        return self._valueItem(category, layer, value, geometry, True, True)
