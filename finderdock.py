"""
Quick Finder
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from qgistools.gui import VectorLayerCombo, FieldCombo
from ui.ui_quickfinder import Ui_quickFinder


class FinderDock(QDockWidget, Ui_quickFinder):
    def __init__(self, iface):
        self.iface = iface
        QDockWidget.__init__(self)
        self.setupUi(self)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self)
        self.layerComboManager = VectorLayerCombo(iface.legendInterface(), self.layerCombo)
        self.fieldComboManager = FieldCombo(self.fieldCombo, self.layerComboManager)
        QObject.connect(self.layerCombo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
        QObject.connect(self.modeButtonGroup, SIGNAL("buttonClicked(int)"), self.layerChanged)
        QObject.connect(self.fieldCombo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
        self.layer = None
        self.operatorBox.hide()
        self.processWidgetGroup.hide()
        self.layerChanged(0)
        self.setVisible(False)

    def layerChanged(self, i):
        self.modeWidgetGroup.setEnabled(False)
        self.searchWidgetGroup.setEnabled(False)
        self.idLine.clear()
        self.layer = self.layerComboManager.getLayer()
        if self.layer is None:
            return
        self.modeWidgetGroup.setEnabled(True)
        if self.fieldButton.isChecked() and self.fieldCombo.currentIndex() == 0:
            return
        self.searchWidgetGroup.setEnabled(True)
        self.on_selectBox_clicked()
               
    @pyqtSignature("on_selectBox_clicked()")
    def on_selectBox_clicked(self):
        if self.layer is None or not self.selectBox.isChecked():
            self.panBox.setEnabled(False)
            self.scaleBox.setEnabled(False)
        else:
            self.panBox.setEnabled(self.layer.hasGeometryType())
            self.scaleBox.setEnabled(self.layer.hasGeometryType() and self.panBox.isChecked())

    @pyqtSignature("on_cancelButton_pressed()")
    def on_cancelButton_pressed(self):
        self.continueSearch = False

    @pyqtSignature("on_goButton_pressed()")
    def on_goButton_pressed(self):
        i = self.layerCombo.currentIndex()
        if i < 1 or self.layer is None:
            return
        toFind = self.idLine.text()
        f = QgsFeature()
        if self.idButton.isChecked():
            id, ok = toFind.toInt()
            if ok is False:
                QMessageBox.warning(self.iface.mainWindow(), "Quick Finder", "ID must be strictly composed of digits.")
                return
            if self.layer.getFeatures(QgsFeatureRequest().setFilterFid(id)).nextFeature(f) is False:
                return
            self.processResults([f.id()])
        else:
            results = []
            fieldName = self.fieldComboManager.getFieldName()
            fieldIndex = self.fieldComboManager.getFieldIndex()
            if fieldName == "":
                return
            operator = self.operatorBox.currentIndex()
            # show progress bar
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(self.layer.featureCount())
            self.progressBar.setValue(0)
            self.processWidgetGroup.show()
            # disable rest of UI
            self.layerWidgetGroup.setEnabled(False)
            self.modeWidgetGroup.setEnabled(False)
            self.searchWidgetGroup.setEnabled(False)
            # create feature request
            featReq = QgsFeatureRequest()
            featReq.setFlags(QgsFeatureRequest.NoGeometry)
            featReq.setSubsetOfAttributes([fieldIndex])
            iter = self.layer.getFeatures(featReq)
            # process
            k = 0
            self.continueSearch = True
            while iter.nextFeature(f) and self.continueSearch:
                k += 1
                value = f.attribute(fieldName)
                if self.evaluate(value, toFind, operator):
                    results.append(f.id())
                self.progressBar.setValue(k)
                QCoreApplication.processEvents()
            # reset UI
            self.processWidgetGroup.hide()
            self.layerWidgetGroup.setEnabled(True)
            self.modeWidgetGroup.setEnabled(True)
            self.searchWidgetGroup.setEnabled(True)
            # process results
            if self.continueSearch:
                self.processResults(results)
                    
    def evaluate(self, v1, v2, operator):
        if operator == 0:
            return v1.toString() == v2
        elif operator == 1:
            return v1.toDouble()[0] == v2.toDouble()[0]
        elif operator == 2:
            return v1.toDouble()[0] <= v2.toDouble()[0]
        elif operator == 3:
            return v1.toDouble()[0] >= v2.toDouble()[0]
        elif operator == 4:
            return v1.toDouble()[0] < v2.toDouble()[0]
        elif operator == 5:
            return v1.toDouble()[0] > v2.toDouble()[0]
        elif operator == 6:
            return v1.toString().contains(v2, Qt.CaseInsensitive)

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
