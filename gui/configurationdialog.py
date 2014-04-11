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

from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QDialog

from qgis.gui import QgsGenericProjectionSelector

from quickfinder.qgissettingmanager import SettingDialog
from quickfinder.core.mysettings import MySettings
from quickfinder.gui.projectsearchdialog import ProjectSearchDialog
from quickfinder.gui.projectlayersmodel import ProjectLayersModel
from quickfinder.ui.ui_configuration import Ui_Configuration


class ConfigurationDialog(QDialog, Ui_Configuration, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()
        SettingDialog.__init__(self, self.settings)

        self.geomapfish_crsButton.clicked.connect(self.geomapfish_crsButtonClicked)

        self.addButton.clicked.connect(self.addProjectSearch)

        self.projectLayersModel = ProjectLayersModel()
        self.projectLayersTable.setModel(self.projectLayersModel)


    def addProjectSearch(self):
        self.dlg = ProjectSearchDialog()
        self.dlg.exec_()


    def geomapfish_crsButtonClicked(self):
        dlg = QgsGenericProjectionSelector(self)
        dlg.setMessage('Select GeoMapFish serveur CRS')
        dlg.setSelectedAuthId(self.geomapfish_crs.text())
        if dlg.exec_():
            self.geomapfish_crs.setText(dlg.selectedAuthId())





