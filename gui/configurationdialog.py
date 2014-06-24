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

from PyQt4.QtGui import QDialog, QFileDialog

from qgis.core import QgsProject
from qgis.gui import QgsGenericProjectionSelector

from os import remove, path

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

        # FTS connection
        self.projectFinder = ProjectFinder(self)

        # table model
        self.projectSearchModel = ProjectSearchModel()
        self.projectSearchTable.setModel(self.projectSearchModel)

        # open/create QuickFinder file
        self.createFileButton.clicked.connect(self.createQFTSfile)
        self.openFileButton.clicked.connect(self.openQFTSfile)
        self.readQFTSfile()

        # project search
        self.addSearchButton.clicked.connect(self.addProjectSearch)
        self.refreshButton.clicked.connect(self.refreshProjectSearch)

        # geomapfish
        self.geomapfishCrsButton.clicked.connect(self.geomapfishCrsButtonClicked)

    def closeEvent(self, e):
        self.projectFinder.close()
        QDialog.closeEvent(self, e)

    def readQFTSfile(self):
        filepath = self.qftsfilepath.text()
        self.projectFinder.setFile(filepath)
        self.projectSearchTable.setEnabled(self.projectFinder.isValid)
        self.projectSearchModel.setSearches(self.projectFinder.searches())

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

    def refreshProjectSearch(self):
        selectedSearchId = []
        for idx in self.projectSearchTable.selectionModel().selectedRows():
            selectedSearchId.append(self.projectSearchModel.data(idx, SearchIdRole))
        RefreshDialog(self.projectFinder, self.projectSearchModel, selectedSearchId).exec_()


    def geomapfishCrsButtonClicked(self):
        dlg = QgsGenericProjectionSelector(self)
        dlg.setMessage('Select GeoMapFish CRS')
        dlg.setSelectedAuthId(self.geomapfishCrs.text())
        if dlg.exec_():
            self.geomapfishCrs.setText(dlg.selectedAuthId())





    # TODO: on exit control that not search are pending