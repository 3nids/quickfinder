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
from PyQt4.QtGui import (QComboBox, QSizePolicy, QTreeView, QIcon, QApplication, QColor,
                         QPushButton, QCursor, QHBoxLayout)

from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
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
        self.rubber.setColor(QColor(255, 255, 50, 200))
        self.rubber.setIcon(self.rubber.ICON_CIRCLE)
        self.rubber.setIconSize(15)
        self.rubber.setWidth(4)
        self.rubber.setBrushStyle(Qt.NoBrush)

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

        self.finders = finders
        for finder in self.finders.values():
            finder.resultFound.connect(self.resultFound)
            finder.limitReached.connect(self.limitReached)
            finder.finished.connect(self.finished)

        self.clearButton = QPushButton(self)
        self.clearButton.setIcon(QIcon(":/plugins/quickfinder/icons/draft.svg"))
        self.clearButton.setText('')
        self.clearButton.setFlat(True)
        self.clearButton.setCursor(QCursor(Qt.ArrowCursor))
        self.clearButton.setStyleSheet('border: 0px; padding: 0px;')
        self.clearButton.clicked.connect(self.clear)

        layout = QHBoxLayout(self)
        self.setLayout(layout)
        layout.addStretch()
        layout.addWidget(self.clearButton)
        layout.addSpacing(20)

        buttonSize = self.clearButton.sizeHint()
        # frameWidth = self.lineEdit().style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        padding = buttonSize.width()  # + frameWidth + 1
        self.lineEdit().setStyleSheet('QLineEdit {padding-right: %dpx; }' % padding)

    def __del__(self):
        if self.rubber:
            self.iface.mapCanvas().scene().removeItem(self.rubber)
            del self.rubber

    def clearSelection(self):
        self.resultModel.setSelected(None, self.resultView.palette())
        self.rubber.reset()

    def clear(self):
        self.clearSelection()
        self.resultModel.clearResults()
        self.lineEdit().setText('')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clearSelection()
        QComboBox.keyPressEvent(self, event)

    def search(self):
        if self.running:
            return

        toFind = self.lineEdit().text()
        if not toFind or toFind == '':
            return

        self.running = True
        self.searchStarted.emit()

        self.clearSelection()
        self.resultModel.clearResults()
        self.resultModel.truncateHistory(MySettings().value("historyLength"))
        self.resultModel.setLoading(True)
        self.showPopup()

        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        self.findersToStart = []
        for finder in self.finders.values():
            if finder.activated():
                self.findersToStart.append(finder)

        bbox = self.mapCanvas.fullExtent()

        while len(self.findersToStart) > 0:
            finder = self.findersToStart[0]
            self.findersToStart.remove(finder)
            self.resultModel.addResult(finder.name)
            finder.start(toFind, bbox=bbox)

        # For case there is no finder activated
        self.finished(None)

    def stop(self):
        self.findersToStart = []
        for finder in self.finders.values():
            if finder.isRunning():
                finder.stop()
        self.finished(None)

    def resultFound(self, finder, layername, value, geometry, srid):
        self.resultModel.addResult(finder.name, layername, value, geometry, srid)
        self.resultView.expandAll()

    def limitReached(self, finder, layername):
        self.resultModel.addEllipsys(finder.name, layername)

    def finished(self, finder):
        if len(self.findersToStart) > 0:
            return
        for finder in self.finders.values():
            if finder.isRunning():
                return

        self.running = False
        self.searchFinished.emit()

        self.resultModel.setLoading(False)

        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

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
            self.clearSelection()

    def transformGeom(self, item):
        src_crs = QgsCoordinateReferenceSystem()
        src_crs.createFromSrid(item.srid)
        dest_crs = self.mapCanvas.mapRenderer().destinationCrs()
        geom = QgsGeometry(item.geometry)
        geom.transform(QgsCoordinateTransform(src_crs, dest_crs))
        return geom

    def zoomToRubberBand(self):
        geom = self.rubber.asGeometry()
        if geom:
            rect = geom.boundingBox()
            rect.scale(1.5)
            self.mapCanvas.setExtent(rect)
            self.mapCanvas.refresh()
