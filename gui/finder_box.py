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

from ..core.mysettings import MySettings
from resultmodel import ResultModel, GroupItem, ResultItem


class FinderBox(QComboBox):

    running = False
    to_finish = 0

    search_started = pyqtSignal()
    search_finished = pyqtSignal()

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

        self.result_view = QTreeView()
        self.result_view.setHeaderHidden(True)
        self.result_view.setMinimumHeight(300)
        self.result_view.activated.connect(self.itemActivated)
        self.result_view.pressed.connect(self.itemPressed)
        self.setView(self.result_view)

        self.result_model = ResultModel(self)
        self.setModel(self.result_model)

        self.finders = finders
        for finder in self.finders.values():
            finder.result_found.connect(self.result_found)
            finder.limit_reached.connect(self.limit_reached)
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

        button_size = self.clearButton.sizeHint()
        # frameWidth = self.lineEdit().style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        padding = button_size.width()  # + frameWidth + 1
        self.lineEdit().setStyleSheet('QLineEdit {padding-right: %dpx; }' % padding)

    def __del__(self):
        if self.rubber:
            self.iface.mapCanvas().scene().removeItem(self.rubber)
            del self.rubber

    def clearSelection(self):
        self.result_model.setSelected(None, self.result_view.palette())
        self.rubber.reset()

    def clear(self):
        self.clearSelection()
        self.result_model.clearResults()
        self.lineEdit().setText('')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clearSelection()
        QComboBox.keyPressEvent(self, event)

    def search(self):
        if self.running:
            return

        to_find = self.lineEdit().text()
        if not to_find or to_find == '':
            return

        self.running = True
        self.search_started.emit()

        self.clearSelection()
        self.result_model.clearResults()
        self.result_model.truncateHistory(MySettings().value("historyLength"))
        self.result_model.setLoading(True)
        self.showPopup()

        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        self.finders_to_start = []
        for finder in self.finders.values():
            if finder.activated():
                self.finders_to_start.append(finder)

        bbox = self.mapCanvas.fullExtent()

        while len(self.finders_to_start) > 0:
            finder = self.finders_to_start[0]
            self.finders_to_start.remove(finder)
            self.result_model.addResult(finder.name)
            finder.start(to_find, bbox=bbox)

        # For case there is no finder activated
        self.finished(None)

    def stop(self):
        self.finders_to_start = []
        for finder in self.finders.values():
            if finder.is_running():
                finder.stop()
        self.finished(None)

    def result_found(self, finder, layername, value, geometry, srid):
        self.result_model.addResult(finder.name, layername, value, geometry, srid)
        self.result_view.expandAll()

    def limit_reached(self, finder, layername):
        self.result_model.addEllipsys(finder.name, layername)

    def finished(self, finder):
        if len(self.finders_to_start) > 0:
            return
        for finder in self.finders.values():
            if finder.is_running():
                return

        self.running = False
        self.search_finished.emit()

        self.result_model.setLoading(False)

        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def itemActivated(self, index):
        item = self.result_model.itemFromIndex(index)
        self.showItem(item)

    def itemPressed(self, index):
        item = self.result_model.itemFromIndex(index)
        if QApplication.mouseButtons() == Qt.LeftButton:
            self.showItem(item)

    def showItem(self, item):
        if isinstance(item, ResultItem):
            self.result_model.setSelected(item, self.result_view.palette())
            geometry = self.transform_geom(item)
            self.rubber.reset(geometry.type())
            self.rubber.setToGeometry(geometry, None)
            self.zoom_to_rubberband()
            return

        if isinstance(item, GroupItem):
            child = item.child(0)
            if isinstance(child, ResultItem):
                self.result_model.setSelected(item, self.result_view.palette())
                self.rubber.reset(child.geometry.type())
                for i in xrange(0, item.rowCount()):
                    geometry = self.transform_geom(item.child(i))
                    self.rubber.addGeometry(geometry, None)
                self.zoom_to_rubberband()
            return

        if item.__class__.__name__ == 'QStandardItem':
            self.clearSelection()

    def transform_geom(self, item):
        src_crs = QgsCoordinateReferenceSystem()
        src_crs.createFromSrid(item.srid)
        dest_crs = self.mapCanvas.mapRenderer().destinationCrs()
        geom = QgsGeometry(item.geometry)
        geom.transform(QgsCoordinateTransform(src_crs, dest_crs))
        return geom

    def zoom_to_rubberband(self):
        geom = self.rubber.asGeometry()
        if geom:
            rect = geom.boundingBox()
            rect.scale(1.5)
            self.mapCanvas.setExtent(rect)
            self.mapCanvas.refresh()
