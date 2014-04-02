'''
Created on 25 mars 2014

@author: arnaud
'''

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon

from .mysettings import MySettings


class GroupItem(QStandardItem):

    name = ''
    count = 0
    more = False

    def __init__(self, name):
        super(GroupItem, self).__init__(name)

        self.name = name
        self.count = 0
        self.more = False

        font = self.font()
        font.setWeight(QFont.Bold)
        self.setFont(font)

        self.setSelectable(False)

    def setName(self, name):
        self.name = name
        self.emitDataChanged()

    def increment(self):
        self.count += 1
        self.emitDataChanged()

    def setMore(self, more):
        self.more = more
        self.emitDataChanged()

    def data(self, role):
        if role == Qt.DisplayRole:
            if self.more:
                return '{0} ({1} ...)'.format(self.name, self.count)
            else:
                return '{0} ({1})'.format(self.name, self.count)
        else:
            return super(GroupItem, self).data(role)


class ResultItem(QStandardItem):

    name = ''
    geometry = None

    def __init__(self, name):
        super(ResultItem, self).__init__(name)
        self.name = name
        self.setSelectable(False)


class ResultModel(QStandardItemModel):

    selected = None

    def __init__(self, parent):
        super(ResultModel, self).__init__(parent)

    def setLoading(self, icon=None):
        root = self.invisibleRootItem()
        item = root.child(0)
        if not icon:
            icon = QIcon()
        item.setIcon(icon)

    def truncateHistory(self, limit):
        root = self.invisibleRootItem()
        for i in xrange(limit, root.rowCount()):
            item = root.child(i)
            if not isinstance(item, GroupItem):
                root.removeRow(item.row())

    def clearResults(self):
        root = self.invisibleRootItem()
        for i in xrange(root.rowCount() - 1, -1, -1):
            item = root.child(i)
            if isinstance(item, GroupItem):
                root.removeRow(item.row())

    def _childItem(self, parent, name, createclass=None):
        for i in xrange(0, parent.rowCount()):
            child = parent.child(i)
            if isinstance(child, createclass) and child.name == name:
                return child

        if createclass:
            child = createclass(name)
            parent.appendRow(child)
            return child

    def addResult(self, category, layer='', value='', geometry=None):
        # print self.__class__.__name__, 'addResult', category, layer, value
        root_item = self.invisibleRootItem()

        category_item = self._childItem(root_item, category, GroupItem)

        if layer == '':
            return
        layer_item = self._childItem(category_item, layer, GroupItem)

        '''
        if layer_item.count >= MySettings().value('limit'):
            self.addEllipsys(category, layer)
            return
        '''

        if value == '':
            return
        category_item.increment()
        layer_item.increment()

        item = ResultItem(value)
        item.geometry = geometry
        layer_item.appendRow(item)

    def addEllipsys(self, category, layer):
        print self.__class__.__name__, 'addEllipsys', category, layer
        root_item = self.invisibleRootItem()

        category_item = self._childItem(root_item, category, GroupItem)

        layer_item = self._childItem(category_item, layer, GroupItem)
        layer_item.setMore(True)

    def setSelected(self, item, palette):
        if self.selected:
            self.selected.setData(self.selected.initialBackgroundColor, Qt.BackgroundColorRole)
            self.selected.setData(self.selected.initialBackgroundColor, Qt.ForegroundRole)

        if item:
            item.initialBackgroundColor = item.data(Qt.BackgroundColorRole)
            item.initialBackgroundColor = item.data(Qt.BackgroundColorRole)
            item.setData(palette.highlight(), Qt.BackgroundColorRole)
            item.setData(palette.highlightedText(), Qt.ForegroundRole)

        self.selected = item
