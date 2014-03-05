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


from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QAction, QDesktopServices, QIcon

from gui.finderdock import FinderDock
from gui.mysettingsdialog import MySettingsDialog

import resources


class quickFinder():
    def __init__(self, iface):
        self.iface = iface
        self.dock = FinderDock(iface)
          
    def initGui(self):
        # dock
        self.dockAction = QAction(QIcon(":/plugins/quickfinder/icons/quickfinder.svg"), "Quick Finder",
                                  self.iface.mainWindow())
        self.dockAction.setCheckable(True)
        self.dockAction.triggered.connect(self.dock.setVisible)
        self.iface.addPluginToMenu("&Quick Finder", self.dockAction)
        self.iface.addToolBarIcon(self.dockAction)
        self.dock.visibilityChanged.connect(self.dockAction.setChecked)
        # settings
        self.settingsAction = QAction(QIcon(":/plugins/quickfinder/icons/settings.svg"), "Settings",
                                      self.iface.mainWindow())
        self.settingsAction.triggered.connect(self.showSettings)
        self.iface.addPluginToMenu("&Quick Finder", self.settingsAction)
        # help
        self.helpAction = QAction(QIcon(":/plugins/quickfinder/icons/help.svg"), "Help", self.iface.mainWindow())
        self.helpAction.triggered.connect(lambda: QDesktopServices().openUrl(QUrl("https://github.com/3nids/quickfinder/wiki")))
        self.iface.addPluginToMenu("&Quick Finder", self.helpAction)

        self.dock.show()
                    
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Quick Finder", self.dockAction)
        self.iface.removePluginMenu("&Quick Finder", self.helpAction)
        self.iface.removePluginMenu("&Quick Finder", self.settingsAction)
        self.iface.removeToolBarIcon(self.dockAction)

        self.dock.close()
        self.dock.deleteLater()

    def showSettings(self):
        MySettingsDialog().exec_()
