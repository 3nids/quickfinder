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

from PyQt4.QtCore import Qt, pyqtSlot, QVariant, QThread
from PyQt4.QtGui import QDockWidget, QMessageBox
from qgis.core import QgsFeature, QgsFeatureRequest, QgsRectangle
from qgis.gui import QgsMessageBar

from ..qgiscombomanager import VectorLayerCombo, ExpressionFieldCombo
from ..core.mysettings import MySettings
from ..core.finderworker import FinderWorker
from ..ui.ui_quickfinder import Ui_quickFinder





class FinderDock(QDockWidget, Ui_quickFinder):
    def __init__(self, iface):
        self.iface = iface
        QDockWidget.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()

        self.layerComboManager = VectorLayerCombo(self.layerCombo)
        self.fieldComboManager = ExpressionFieldCombo(self.fieldCombo, self.expressionButton, self.layerComboManager)

        self.layerComboManager.layerChanged.connect(self.layerChanged)
        self.fieldCombo.activated.connect(self.fieldChanged)

        self.layer = None

        self.progressWidget.hide()
        self.fieldWidget.setEnabled(False)
        self.searchWidget.setEnabled(False)



        self.layerChanged()

        if MySettings().value("dockArea") == 1:
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        else:
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self)

    def showEvent(self, e):
        layer = self.iface.legendInterface().currentLayer()
        self.layerComboManager.setLayer(layer)

    def displayMessage(self, message, level):
        self.iface.messageBar().pushMessage("Quick Finder", message, level, 3)

    def layerChanged(self):
        print "layerChanged"
        self.searchWidget.setEnabled(False)
        self.fieldWidget.setEnabled(False)
        self.layer = self.layerComboManager.getLayer()
        if self.layer is None:
            return
        self.fieldWidget.setEnabled(True)

    def fieldChanged(self):
        print "fieldchanged"
        self.searchWidget.setEnabled(False)
        if self.layer is None:
            return
        field, isExpression = self.fieldComboManager.getExpression()
        print field
        if field is None:
            print "ret"
            return
        self.searchWidget.setEnabled(True)
        if not isExpression:
            fieldType = self.layer.pendingFields().field(field).type()
            # if field is a string set operator to "LIKE"
            if fieldType == QVariant.String:
                self.operatorBox.setCurrentIndex(6)
            # if field is not string, do not use "LIKE"
            if fieldType != QVariant.String and self.operatorBox.currentIndex() == 6:
                self.operatorBox.setCurrentIndex(0)
            return
        # is expression, use string by default
        self.operator.setCurrentIndex(6)

    def searchFinished(self):
        self.progressWidget.hide()

    @pyqtSlot(name="on_searchEdit_returnPressed")
    def search(self):
        self.thread = QThread()
        self.worker = FinderWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.find)
        self.thread.finished.connect(self.searchFinished)
        self.worker.progress.connect(self.progressBar.setValue)
        self.cancelButton.clicked.connect(self.worker.stop)
        self.worker.message.connect(self.displayMessage)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.searchEdit.returnPressed.connect(self.worker.stop)


        # give search parameters to thread
        self.layer = self.layerComboManager.getLayer()
        if self.layer is None:
            return
        field, isExpression = self.fieldComboManager.getExpression()
        if field is None:
            return
        toFind = self.searchEdit.text()
        operator = self.operatorBox.currentIndex()
        self.worker.define(self.layer, field, isExpression, operator, toFind)

        # show progress bar
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(self.layer.pendingFeatureCount())
        self.progressBar.setValue(0)
        self.progressWidget.show()

        # start
        self.thread.start()

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

