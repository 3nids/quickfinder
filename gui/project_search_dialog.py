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
from ..ui.ui_projectsearch import Ui_ProjectSearch


class ProjectSearchDialog(QDialog, Ui_ProjectSearch):
    def __init__(self, project_finder, project_search_model, projectSearch=None):
        QDialog.__init__(self)
        self.setupUi(self)

        self.project_finder = project_finder
        self.project_search_model = project_search_model
        self.projectSearch = projectSearch

        self.layerCombo.setFilters(QgsMapLayerProxyModel.HasGeometry)
        self.layerCombo.layerChanged.connect(self.fieldExpressionWidget.setLayer)
        self.fieldExpressionWidget.setLayer(self.layerCombo.currentLayer())

        self.progressBar.hide()
        self.cancelButton.hide()
        self.cancelButton.clicked.connect(self.project_finder.stop_record)
        self.okButton.clicked.connect(self.process)

        self.project_finder.recordingSearchProgress.connect(self.progressBar.setValue)

        if projectSearch is not None:
            self.searchName.setText(projectSearch.searchName)
            self.layerCombo.setLayer(projectSearch.layer())
            self.fieldExpressionWidget.setField(projectSearch.expression)
            self.priorityBox.setValue(projectSearch.priority)

    def process(self):
        search_name = self.searchName.text()
        layer = self.layerCombo.currentLayer()
        expression = self.fieldExpressionWidget.currentField()[0]
        priority = self.priorityBox.value()
        srid = layer.crs().authid()
        evaluate_directly = self.evaluateCheckBox.isChecked()

        if self.projectSearch is None:
            self.projectSearch = self.project_search_model.addSearch(search_name, layer, expression, priority)
        else:
            self.projectSearch.edit(search_name, layer.id(), layer.name(), expression, priority, srid)

        if evaluate_directly:
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(layer.featureCount())
            self.progressBar.show()
            self.cancelButton.show()

            ok, message = self.project_finder.recordSearch(self.projectSearch)

            self.progressBar.hide()
            self.cancelButton.hide()
            self.okButton.show()

            if not ok:
                QErrorMessage().showMessage(message)
                return

        self.close()