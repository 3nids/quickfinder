'''
Created on 24 mars 2014

@author: arnaud
'''

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem

class ResultsTree(QTreeWidget):

    def __init__(self, params):
        QTreeWidget.__init__(self)
        self.setHeaderHidden(True)
        self.itemClicked.connect(self.onItemClicked)

    def clear(self):
        QTreeWidget.clear(self)

    def getCategoryItem(self, category, create=True):
        for i in xrange(0, self.topLevelItemCount()):
            if self.topLevelItem(i).text(1) == category:
                return self.topLevelItem(i)
        if not create:
            return None
        item = QTreeWidgetItem(self)
        item.setText(0, category)
        item.setText(1, category)
        item.setData(0, Qt.UserRole, 0)
        item.setExpanded(True)
        self.addTopLevelItem(item)
        return item

    def getLayerItem(self, category, layername, create=True):
        cat_item = self.getCategoryItem(category, create)

        for i in xrange(0, cat_item.childCount()):
            if cat_item.child(i).text(1) == layername:
                return cat_item.child(i)
        if not create:
            return None
        item = QTreeWidgetItem(cat_item)
        item.setText(0, layername)
        item.setText(1, layername)
        item.setData(0, Qt.UserRole, 0)
        item.setExpanded(True)
        return item

    def addResult(self, category, layername, value, geometry):
        layer_item = self.getLayerItem(category, layername, True)

        item = QTreeWidgetItem(layer_item)  # , value, feature)
        item.setText(0, value)
        item.setData(0, Qt.UserRole, geometry)

        layer_count = layer_item.data(0, Qt.UserRole) + 1
        layer_item.setText(0, '{0} ({1})'.format(layername, layer_count))
        layer_item.setData(0, Qt.UserRole, layer_count)

        category_item = layer_item.parent()
        category_count = category_item.data(0, Qt.UserRole) + 1
        category_item.setText(0, '{0} ({1})'.format(category, category_count))
        category_item.setData(0, Qt.UserRole, category_count)

    def onItemClicked(self, item, column):
        test = item.data(0, Qt.UserRole)
        test = test
