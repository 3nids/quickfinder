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

from os import remove, path

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import (QDialog, QFileDialog, QMessageBox,
                        QSortFilterProxyModel, QHeaderView)

from qgis.core import QgsProject
from qgis.gui import QgsGenericProjectionSelector

from ..qgissettingmanager import SettingDialog
from ..core.my_settings import MySettings
from ..core.project_finder import ProjectFinder, create_FTS_file
from project_search_dialog import ProjectSearchDialog
from project_search_model import ProjectSearchModel, SearchIdRole
from refresh_dialog import RefreshDialog
from ..ui.ui_configuration import Ui_Configuration


class ConfigurationDialog(QDialog, Ui_Configuration, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()
        SettingDialog.__init__(self, self.settings)

        # new declaration of ProjectFinder since changes can be cancelled
        self.project_finder = ProjectFinder(self)

        # table model
        self.project_search_model = ProjectSearchModel(self.project_finder)

        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.project_search_model)
        self.projectSearchTable.setModel(self.proxyModel)

        header = self.projectSearchTable.horizontalHeader()
        header.setResizeMode(QHeaderView.ResizeToContents)

        # open/create QuickFinder file
        self.createFileButton.clicked.connect(self.create_QFTS_file)
        self.openFileButton.clicked.connect(self.open_QFTS_file)
        self.read_QFTS_file()

        # project search
        self.addSearchButton.clicked.connect(self.add_project_search)
        self.removeSearchButton.clicked.connect(self.remove_project_search)
        self.editSearchButton.clicked.connect(self.edit_project_search)
        self.refreshButton.clicked.connect(self.refresh_project_search)
        self.projectSearchTable.selectionModel().selectionChanged.connect(self.enableButtons)
        self.enableButtons()

        # geomapfish
        self.geomapfishCrsButton.clicked.connect(self.geomapfishCrsButtonClicked)

    def reject(self):
        if self.close_and_control():
            QDialog.reject(self)

    def accept(self):
        if self.close_and_control():
            QDialog.accept(self)

    def close_and_control(self):
        self.project_finder.close()
        for search in self.project_finder.searches.values():
            if search.dateEvaluated is None:
                box = QMessageBox(QMessageBox.Warning,
                                  "Quick Finder",
                                  QCoreApplication.translate("Configuration dialog", "Some searches are still not recorded to the file. Do you want to record them now ? "),
                                  QMessageBox.Cancel | QMessageBox.Yes | QMessageBox.Close,
                                  self)
                ret = box.exec_()
                if ret == QMessageBox.Cancel:
                    return False
                elif ret == QMessageBox.Yes:
                    self.refresh_project_search()
                    return False
        return True

    def read_QFTS_file(self):
        filepath = self.qftsfilepath.text()
        self.project_finder.setFile(filepath)
        self.projectSearchTable.setEnabled(self.project_finder.isValid)
        self.projectSearchButtonsWidget.setEnabled(self.project_finder.isValid)

    def create_QFTS_file(self):
        prjPath = QgsProject.instance().homePath()
        filepath = QFileDialog.getSaveFileName(self, "Create Quickfinder index file", prjPath,
                                               "Quickfinder file (*.qfts)")
        if filepath:
            if filepath[-5:] != ".qfts":
                filepath += ".qfts"
            if path.isfile(filepath):
                remove(filepath)
            create_FTS_file(filepath)
            self.qftsfilepath.setText(filepath)
            self.read_QFTS_file()

    def open_QFTS_file(self):
        prjPath = QgsProject.instance().homePath()
        filepath = QFileDialog.getOpenFileName(self, "Open Quickfinder index file",
                                               prjPath, "Quickfinder file (*.qfts)")
        if filepath:
            self.qftsfilepath.setText(filepath)
            self.read_QFTS_file()

    def add_project_search(self):
        ProjectSearchDialog(self.project_finder, self.project_search_model).exec_()

    def remove_project_search(self):
        sel = self.selected_search_ids()
        if len(sel) == 0:
            return
        box = QMessageBox(QMessageBox.Warning,
                                  "Quick Finder",
                                  QCoreApplication.translate("Configuration dialog", "Are you sure to remove {0} search(es) ? ").format(len(sel)),
                                  QMessageBox.Yes | QMessageBox.Cancel,
                                  self)
        ret = box.exec_()
        if ret == QMessageBox.Cancel:
            return
        self.project_search_model.removeSearches(sel)

    def edit_project_search(self):
        sel = self.selected_search_ids()
        if len(sel) != 1:
            return
        if not self.project_search_model.searches.has_key(sel[0]):
            return
        search = self.project_search_model.searches[sel[0]]
        if search:
            ProjectSearchDialog(self.project_finder, self.project_search_model, search).exec_()

    def refresh_project_search(self):
        RefreshDialog(self.project_finder, self.project_search_model, self.selected_search_ids()).exec_()

    def selected_search_ids(self):
        selectedSearchId = []
        for idx in self.projectSearchTable.selectionModel().selectedRows():
            selectedSearchId.append(self.proxyModel.data(idx, SearchIdRole))
        return selectedSearchId

    def enableButtons(self):
        n = len(self.selected_search_ids())
        self.removeSearchButton.setEnabled(n > 0)
        self.editSearchButton.setEnabled(n == 1)
        self.projectSearchButtonsWidget.setEnabled(self.project_finder.isValid)

    def geomapfishCrsButtonClicked(self):
        dlg = QgsGenericProjectionSelector(self)
        dlg.setMessage('Select GeoMapFish CRS')
        dlg.setSelectedAuthId(self.geomapfishCrs.text())
        if dlg.exec_():
            self.geomapfishCrs.setText(dlg.selectedAuthId())
