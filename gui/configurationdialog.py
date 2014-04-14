#-----------------------------------------------------------
#
# Item Browser is a QGIS plugin which allows you to browse a multiple selection.
#
# Copyright    : (C) 2013 Denis Rouzaud
# Email        : denis.rouzaud@gmail.com
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
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtGui import QDialog, QFileDialog

from qgis.core import QgsProject
from qgis.gui import QgsGenericProjectionSelector

from os import remove, path

from quickfinder.qgissettingmanager import SettingDialog
from quickfinder.core.mysettings import MySettings
from quickfinder.core.ftsconnection import FtsConnection, createFTSfile
from quickfinder.gui.projectsearchdialog import ProjectSearchDialog
from quickfinder.gui.localsearchmodel import LocalSearchModel
from quickfinder.ui.ui_configuration import Ui_Configuration


class ConfigurationDialog(QDialog, Ui_Configuration, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()
        SettingDialog.__init__(self, self.settings)

        # table model
        self.localSearchModel = LocalSearchModel()
        self.localSearchTable.setModel(self.localSearchModel)

        # open/create QuickFinder file
        self.createFileButton.clicked.connect(self.createQFTSfile)
        self.openFileButton.clicked.connect(self.openQFTSfile)
        self.readQFTSfile()

        # add local search
        self.addSearchButton.clicked.connect(self.addProjectSearch)

        # geomapfish
        self.geomapfish_crsButton.clicked.connect(self.geomapfish_crsButtonClicked)

    def readQFTSfile(self):
        filepath = self.qftsfilepath.text()
        fts = FtsConnection(filepath)
        print filepath, fts.isValid
        self.localSearchTable.setEnabled(fts.isValid)
        self.localSearchModel.setFtsConnection(fts)

    def createQFTSfile(self):
        prjPath = QgsProject.instance().homePath()
        filepath = QFileDialog.getSaveFileName(self, "Create Quickfinder index file", prjPath, "Quickfinder file (*.qfts)")
        if filepath:
            if path.isfile(filepath):
                remove(filepath)
            createFTSfile(filepath)
            self.qftsfilepath.setText(filepath)
            self.readQFTSfile()

    def openQFTSfile(self):
        prjPath = QgsProject.instance().homePath()
        filepath = QFileDialog.getOpenFileName(self, "Create Quickfinder index file", prjPath, "Quickfinder file (*.qfts)")
        if filepath:
            self.qftsfilepath.setText(filepath)
            self.readQFTSfile()

    def addProjectSearch(self):
        self.dlg = ProjectSearchDialog()
        if self.dlg.exec_():
            name = self.dlg.searchName.text()
            layer = self.dlg.layerCombo.currentLayer()
            expression = self.dlg.fieldCombo.currentField()[0]
            priority = self.dlg.priorityBox.value()
            evaluateDirectly = self.dlg.evaluateCheckBox.isChecked()
            self.localSearchModel.addSearch(name, layer.id(), layer.name(), expression, priority, evaluateDirectly)


    def geomapfish_crsButtonClicked(self):
        dlg = QgsGenericProjectionSelector(self)
        dlg.setMessage('Select GeoMapFish serveur CRS')
        dlg.setSelectedAuthId(self.geomapfish_crs.text())
        if dlg.exec_():
            self.geomapfish_crs.setText(dlg.selectedAuthId())





