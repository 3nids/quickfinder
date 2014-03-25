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

from PyQt4.QtCore import Qt, pyqtSlot
from PyQt4.QtGui import QDockWidget, QMessageBox, QTreeView
from qgis.core import (QgsFeature, QgsFeatureRequest, QgsRectangle)
from qgis.gui import QgsMessageBar

from quickfinder.core.resultmodel import ResultModel
from quickfinder.core.projectfinder import ProjectFinder
from quickfinder.core.osmfinder import OsmFinder
from quickfinder.core.mysettings import MySettings
from quickfinder.gui.resultstree import ResultsTree
from quickfinder.ui.ui_quickfinder import Ui_quickFinder

class FinderDock(QDockWidget, Ui_quickFinder):

    finders = {}

    def __init__(self, iface):
        self.iface = iface
        QDockWidget.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()

        self.searchButton.clicked.connect(self.onSearchButtonClicked)

        self.resultsTree = ResultsTree(self)
        self.resultsWidget.layout().addWidget(self.resultsTree)

        self.resultModel = ResultModel(self.searchBox)
        self.searchBox.setModel(self.resultModel)

        self.resultView = QTreeView()
        self.resultView.setHeaderHidden(True)
        self.searchBox.setView(self.resultView)

        self.progressWidget.hide()

        # self.searchWidget.setEnabled(False)
        self.finders['project'] = ProjectFinder()
        self.finders['osm'] = OsmFinder()

        for finder in self.finders.values():
            finder.resultFound.connect(self.resultFound)
            finder.message.connect(self.displayMessage)
            finder.finished.connect(self.searchFinished)
            self.cancelButton.clicked.connect(finder.stop)

        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self)

    def displayMessage(self, message, level):
        self.iface.messageBar().pushMessage("Quick Finder", message, level, 3)

    def searchFinished(self):
        self.progressWidget.hide()
        self.stop()

    def onSearchButtonClicked(self, checked):
        if checked:
            self.search()
        else:
            self.stop()

    def stop(self):
        for finder in self.finders.values():
            finder.stop()

        self.searchButton.setChecked(False)
        self.searchButton.setText(self.tr('search'))

    @pyqtSlot(name="on_searchEdit_returnPressed")
    def search(self):
        self.stop()
        self.resultsTree.clear()
        self.resultModel.clear()

        self.searchButton.setChecked(True)
        self.searchButton.setText(self.tr('stop'))

        '''
        # show progress bar
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(self.layer.pendingFeatureCount())
        self.progressBar.setValue(0)
        self.progressWidget.show()
        '''

        toFind = self.searchEdit.text()
        '''
        for finder in self.finders.values():
            finder.start(toFind)
        '''
        self.finders['project'].start(toFind)

        self.searchBox.showPopup()

    def resultFound(self, category, layername, value, geometry):
        self.resultsTree.addResult(category, layername, value, geometry)

        self.resultModel.addResult(category, layername, value, geometry)
        self.resultView.expandAll()

    def processResults(self, results):
        if self.layer is None:
            return
        if self.selectBox.isChecked():
            self.layer.setSelectedFeatures(results)
            if len(results) == 0:
                return

            if self.panBox.isEnabled() and self.panBox.isChecked():
                canvas = self.iface.mapCanvas()
                rect = canvas.mapRenderer().layerExtentToOutputExtent(self.layer, self.layer.boundingBoxOfSelected())
                if rect is not None:
                    if self.scaleBox.isEnabled() and self.scaleBox.isChecked():
                        rect.scale(1.5)
                        canvas.setExtent(rect)
                    else:
                        canvas.setExtent(QgsRectangle(rect.center(), rect.center()))
                canvas.refresh()
        if self.formBox.isChecked():
            nResults = len(results)
            if nResults > 25:
                return
            if nResults > 3:
                reply = QMessageBox.question(self.iface.mainWindow(), "Quick Finder",
                                             "%s results were found. Are you sure to open the %s feature forms ?" %
                                             (nResults, nResults), QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            f = QgsFeature()
            for id in results:
                if self.layer.getFeatures(QgsFeatureRequest().setFilterFid(id)).nextFeature(f):
                    self.iface.openFeatureForm(self.layer, f)

