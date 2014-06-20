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
from PyQt4.QtGui import QComboBox, QSizePolicy, QTreeView, QIcon, QApplication

from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.gui import QgsRubberBand

from quickfinder.core.mysettings import MySettings
from quickfinder.gui.resultmodel import ResultModel, GroupItem, ResultItem


class FinderBox(QComboBox):

    running = False
    toFinish = 0

    searchStarted = pyqtSignal()
    searchFinished = pyqtSignal()

    def __init__(self, finders, iface, parent=None):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        self.rubber = QgsRubberBand(self.mapCanvas)

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
        for finder in self.finders.itervalues():
            if finder.activated():
                self.resultModel.addResult(finder.name)
                self.toFinish += 1

        bbox = self.mapCanvas.fullExtent()
        for finder in self.finders.itervalues():
            if finder.activated():
                finder.start(toFind, bbox=bbox)

    def stop(self):
        for finder in self.finders.itervalues():
            if finder.isRunning():
                finder.stop()

    def resultFound(self, finder, layername, value, geometry, epsg):
        self.resultModel.addResult(finder.name, layername, value, geometry, epsg)
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
            geometry = self.transformGeom(item)
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
                    geometry = self.transformGeom(item.child(i))
                    self.rubber.addGeometry(geometry, None)
                self.zoomToRubberBand()
            return

        if item.__class__.__name__ == 'QStandardItem':
            self.resultModel.setSelected(None, self.resultView.palette())
            self.rubber.reset()
            return

    def transformGeom(self, item):
        geometry = item.geometry
        src_crs = QgsCoordinateReferenceSystem()
        src_crs.createFromSrid(item.epsg)
        dest_crs = self.mapCanvas.mapRenderer().destinationCrs()
        geom = item.geometry
        geom.transform( QgsCoordinateTransform(src_crs, dest_crs) )
        return geom

    def zoomToRubberBand(self):
        rect = self.rubber.asGeometry().boundingBox()
        rect.scale(1.5)
        self.mapCanvas.setExtent(rect)
        self.mapCanvas.refresh()
