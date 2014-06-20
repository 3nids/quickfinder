#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2014 Denis Rouzaud, Anrnaud Morvan
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

from PyQt4.QtCore import Qt, QCoreApplication, pyqtSignal, QEventLoop
from PyQt4.QtGui import QComboBox, QSizePolicy, QTreeView, QIcon

from quickfinder.core.mysettings import MySettings

from quickfinder.gui.resultmodel import ResultModel, GroupItem, ResultItem


class FinderBox(QComboBox):

    running = False
    toFinish = 0

    searchStarted = pyqtSignal()
    searchFinished = pyqtSignal()

    def __init__(self, finders, iface, parent=None):
        self.iface = iface

        QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertAtTop)
        self.setMinimumHeight(27)
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Fixed)

        self.insertSeparator(0)
        self.lineEdit().returnPressed.connect(self.search)

        self.resultView = QTreeView()
        self.resultView.setHeaderHidden(True)
        self.resultView.setMinimumHeight(300)
        self.resultView.activated.connect(self.itemActivated)
        self.resultView.pressed.connect(self.itemPressed)
        self.setView(self.resultView)

        self.resultModel = ResultModel(self)
        self.setModel(self.resultModel)

        self.loadingIcon = QIcon(":/plugins/quickfinder/icons/loading.gif")

        self.finders = finders
        for finder in self.finders.itervalues():
            finder.resultFound.connect(self.resultFound)
            finder.limitReached.connect(self.limitReached)
            finder.finished.connect(self.finished)
            finder.message.connect(self.message)

    def search(self):
        if self.running:
            return

        toFind = self.lineEdit().text()
        if not toFind:
            return

        self.running = True
        self.searchStarted.emit()

        self.resultModel.clearResults()
        self.resultModel.truncateHistory(MySettings().value("historyLength"))
        self.resultModel.setLoading(self.loadingIcon)
        self.showPopup()

        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        # create categories in special order and count activated ones
        for key in ['project', 'geomapfish', 'osm']:
            finder = self.finders[key]
            if finder.activated():
                self.resultModel.addResult(finder.name)
                self.toFinish += 1

        canvas = self.iface.mapCanvas()
        crs = canvas.mapRenderer().destinationCrs()
        bbox = canvas.fullExtent()
        for finder in self.finders.itervalues():
            if finder.activated():
                finder.start(toFind, crs=crs, bbox=bbox)

    def stop(self):
        for finder in self.finders.itervalues():
            if finder.isRunning():
                finder.stop()

    def resultFound(self, finder, layername, value, geometry):
        self.resultModel.addResult(finder.name, layername, value, geometry)
        self.resultView.expandAll()

    def limitReached(self, finder, layername):
        self.resultModel.addEllipsys(finder.name, layername)

    def finished(self, finder):
        # wait for all running finders
        '''
        for finder in self.finders.itervalues():
            if finder.isRunning():
                return
        '''
        self.toFinish -= 1
        if self.toFinish > 0:
            return

        self.running = False
        self.searchFinished.emit()

        self.resultModel.setLoading(None)

        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def message(self, finder, message, level):
        self.iface.messageBar().pushMessage("Quick Finder", message, level, 3)

    def itemActivated(self, index):
        item = self.resultModel.itemFromIndex(index)
        self.showItem(item)

    def itemPressed(self, index):
        item = self.resultModel.itemFromIndex(index)
        if QApplication.mouseButtons() == Qt.LeftButton:
            self.showItem(item)

    def showItem(self, item):
        if isinstance(item, ResultItem):
            self.resultModel.setSelected(item, self.resultView.palette())
            geometry = item.geometry
            self.rubber.reset(geometry.type())
            self.rubber.setToGeometry(geometry, None)
            self.zoomToRubberBand()
            return

        if isinstance(item, GroupItem):
            child = item.child(0)
            if isinstance(child, ResultItem):
                self.resultModel.setSelected(item, self.resultView.palette())
                self.rubber.reset(child.geometry.type())
                for i in xrange(0, item.rowCount()):
                    child = item.child(i)
                    self.rubber.addGeometry(item.child(i).geometry, None)
                self.zoomToRubberBand()
            return

        if item.__class__.__name__ == 'QStandardItem':
            self.resultModel.setSelected(None, self.resultView.palette())
            self.rubber.reset()
            return

    def zoomToRubberBand(self):
        rect = self.rubber.asGeometry().boundingBox()
        rect.scale(1.5)
        self.iface.mapCanvas().setExtent(rect)
        self.iface.mapCanvas().refresh()
