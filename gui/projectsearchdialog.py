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

from PyQt4.QtGui import QDialog, QErrorMessage

from qgis.gui import QgsMapLayerProxyModel

from quickfinder.ui.ui_projectsearch import Ui_ProjectSearch


class ProjectSearchDialog(QDialog, Ui_ProjectSearch):
    def __init__(self, projectFinder, projectSearchModel, projectSearch=None):
        QDialog.__init__(self)
        self.setupUi(self)

        self.projectFinder = projectFinder
        self.projectSearchModel = projectSearchModel
        self.projectSearch = projectSearch

        self.layerCombo.setFilters(QgsMapLayerProxyModel.HasGeometry)
        self.layerCombo.layerChanged.connect(self.fieldExpressionWidget.setLayer)
        self.fieldExpressionWidget.setLayer(self.layerCombo.currentLayer())

        self.progressBar.hide()
        self.cancelButton.hide()
        self.cancelButton.clicked.connect(self.projectFinder.stopRecord)
        self.okButton.clicked.connect(self.process)

        self.projectFinder.recordingSearchProgress.connect(self.progressBar.setValue)

        if projectSearch is not None:
            self.searchName.setText(projectSearch.searchName)
            self.layerCombo.setLayer(projectSearch.layer())
            self.fieldExpressionWidget.setField(projectSearch.expression)
            self.priorityBox.setValue(projectSearch.priority)

    def process(self):
        searchName = self.searchName.text()
        layer = self.layerCombo.currentLayer()
        expression = self.fieldExpressionWidget.currentField()[0]
        priority = self.priorityBox.value()
        srid = layer.crs().authid()
        evaluateDirectly = self.evaluateCheckBox.isChecked()

        if self.projectSearch is None:
            self.projectSearch = self.projectSearchModel.addSearch(searchName, layer, expression, priority)
        else:
            self.projectSearch.edit(searchName, layer.id(), layer.name(), expression, priority, srid)

        if evaluateDirectly:
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(layer.featureCount())
            self.progressBar.show()
            self.cancelButton.show()

            ok, message = self.projectFinder.recordSearch(self.projectSearch)

            self.progressBar.hide()
            self.cancelButton.hide()
            self.okButton.show()

            if not ok:
                QErrorMessage().showMessage(message)
                return

        self.close()