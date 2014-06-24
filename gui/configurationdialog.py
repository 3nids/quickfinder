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
from quickfinder.core.localfinder import LocalFinder, createFTSfile
from quickfinder.gui.projectsearchdialog import ProjectSearchDialog
from quickfinder.gui.localsearchmodel import LocalSearchModel
from quickfinder.gui.refreshdialog import RefreshDialog
from quickfinder.ui.ui_configuration import Ui_Configuration


class ConfigurationDialog(QDialog, Ui_Configuration, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()
        SettingDialog.__init__(self, self.settings)

        # FTS connection
        self.localFinder = LocalFinder(self)

        # table model
        self.localSearchModel = LocalSearchModel()
        self.localSearchTable.setModel(self.localSearchModel)

        # open/create QuickFinder file
        self.createFileButton.clicked.connect(self.createQFTSfile)
        self.openFileButton.clicked.connect(self.openQFTSfile)
        self.readQFTSfile()

        # local search
        self.addSearchButton.clicked.connect(self.addProjectSearch)
        self.refreshButton.clicked.connect(self.refreshLocalSearch)

        # geomapfish
        self.geomapfishCrsButton.clicked.connect(self.geomapfishCrsButtonClicked)

    def closeEvent(self, e):
        self.localFinder.close()
        QDialog.closeEvent(self, e)

    def readQFTSfile(self):
        filepath = self.qftsfilepath.text()
        self.localFinder.setFile(filepath)
        self.localSearchTable.setEnabled(self.localFinder.isValid)
        self.localSearchModel.setSearches(self.localFinder.searches())

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
        ProjectSearchDialog(self.localFinder, self.localSearchModel).exec_()

    def refreshLocalSearch(self):
        RefreshDialog(self.localFinder, self.localSearchModel).exec_()


    def geomapfishCrsButtonClicked(self):
        dlg = QgsGenericProjectionSelector(self)
        dlg.setMessage('Select GeoMapFish CRS')
        dlg.setSelectedAuthId(self.geomapfishCrs.text())
        if dlg.exec_():
            self.geomapfishCrs.setText(dlg.selectedAuthId())





    # TODO: on exit control that not search are pending