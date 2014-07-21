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

from quickfinder.qgissettingmanager import SettingDialog
from quickfinder.core.mysettings import MySettings
from quickfinder.core.projectfinder import ProjectFinder, createFTSfile
from quickfinder.gui.projectsearchdialog import ProjectSearchDialog
from quickfinder.gui.projectsearchmodel import ProjectSearchModel, SearchIdRole
from quickfinder.gui.refreshdialog import RefreshDialog
from quickfinder.ui.ui_configuration import Ui_Configuration


class ConfigurationDialog(QDialog, Ui_Configuration, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()
        SettingDialog.__init__(self, self.settings)

        # new declaration of ProjectFinder since changes can be cancelled
        self.projectFinder = ProjectFinder(self)

        # table model
        self.projectSearchModel = ProjectSearchModel(self.projectFinder)

        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.projectSearchModel)
        self.projectSearchTable.setModel(self.proxyModel)

        header = self.projectSearchTable.horizontalHeader()
        header.setResizeMode(QHeaderView.ResizeToContents)

        # open/create QuickFinder file
        self.createFileButton.clicked.connect(self.createQFTSfile)
        self.openFileButton.clicked.connect(self.openQFTSfile)
        self.readQFTSfile()

        # project search
        self.addSearchButton.clicked.connect(self.addProjectSearch)
        self.removeSearchButton.clicked.connect(self.removeProjectSearch)
        self.editSearchButton.clicked.connect(self.editProjectSearch)
        self.refreshButton.clicked.connect(self.refreshProjectSearch)
        self.projectSearchTable.selectionModel().selectionChanged.connect(self.enableButtons)
        self.enableButtons()

        # geomapfish
        self.geomapfishCrsButton.clicked.connect(self.geomapfishCrsButtonClicked)

    def reject(self):
        if self.closeAndControl():
            QDialog.reject(self)

    def accept(self):
        if self.closeAndControl():
            QDialog.accept(self)

    def closeAndControl(self):
        self.projectFinder.close()
        for search in self.projectFinder.searches.values():
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
                    self.refreshProjectSearch()
                    return False
        return True

    def readQFTSfile(self):
        filepath = self.qftsfilepath.text()
        self.projectFinder.setFile(filepath)
        self.projectSearchTable.setEnabled(self.projectFinder.isValid)
        self.projectSearchButtonsWidget.setEnabled(self.projectFinder.isValid)

    def createQFTSfile(self):
        prjPath = QgsProject.instance().homePath()
        filepath = QFileDialog.getSaveFileName(self, "Create Quickfinder index file", prjPath,
                                               "Quickfinder file (*.qfts)")
        if filepath:
            if filepath[-5:] != ".qfts":
                filepath += ".qfts"
            if path.isfile(filepath):
                remove(filepath)
            createFTSfile(filepath)
            self.qftsfilepath.setText(filepath)
            self.readQFTSfile()

    def openQFTSfile(self):
        prjPath = QgsProject.instance().homePath()
        filepath = QFileDialog.getOpenFileName(self, "Open Quickfinder index file",
                                               prjPath, "Quickfinder file (*.qfts)")
        if filepath:
            self.qftsfilepath.setText(filepath)
            self.readQFTSfile()

    def addProjectSearch(self):
        ProjectSearchDialog(self.projectFinder, self.projectSearchModel).exec_()

    def removeProjectSearch(self):
        sel = self.selectedSearchIds()
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
        self.projectSearchModel.removeSearches(sel)

    def editProjectSearch(self):
        sel = self.selectedSearchIds()
        if len(sel) != 1:
            return
        if not self.projectSearchModel.searches.has_key(sel[0]):
            return
        search = self.projectSearchModel.searches[sel[0]]
        if search:
            ProjectSearchDialog(self.projectFinder, self.projectSearchModel, search).exec_()

    def refreshProjectSearch(self):
        RefreshDialog(self.projectFinder, self.projectSearchModel, self.selectedSearchIds()).exec_()

    def selectedSearchIds(self):
        selectedSearchId = []
        for idx in self.projectSearchTable.selectionModel().selectedRows():
            selectedSearchId.append(self.proxyModel.data(idx, SearchIdRole))
        return selectedSearchId

    def enableButtons(self):
        n = len(self.selectedSearchIds())
        self.removeSearchButton.setEnabled(n > 0)
        self.editSearchButton.setEnabled(n == 1)
        self.projectSearchButtonsWidget.setEnabled(self.projectFinder.isValid)

    def geomapfishCrsButtonClicked(self):
        dlg = QgsGenericProjectionSelector(self)
        dlg.setMessage('Select GeoMapFish CRS')
        dlg.setSelectedAuthId(self.geomapfishCrs.text())
        if dlg.exec_():
            self.geomapfishCrs.setText(dlg.selectedAuthId())
