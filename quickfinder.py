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


from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtGui import QAction, QDesktopServices, QIcon

import resources

from finderdock import FinderDock


class quickFinder():
    def __init__(self, iface):
        self.iface = iface
        self.dock = FinderDock(iface)
          
    def initGui(self):
        # dock
        self.dockAction = QAction(QIcon(":/plugins/quickfinder/icons/quickfinder.png"), "Quick Finder",
                                  self.iface.mainWindow())
        self.dockAction.setCheckable(True)
        QObject.connect(self.dockAction, SIGNAL("triggered(bool)"), self.dock.setVisible)
        self.iface.addPluginToMenu("&Quick Finder", self.dockAction)
        self.iface.addToolBarIcon(self.dockAction)
        QObject.connect(self.dock, SIGNAL("visibilityChanged(bool)"), self.dockAction.setChecked)
        # help
        self.helpAction = QAction(QIcon(":/plugins/quickfinder/icons/help.png"), "Help", self.iface.mainWindow())
        QObject.connect(self.helpAction, SIGNAL("triggered()"),
                        lambda: QDesktopServices().openUrl(QUrl("https://github.com/3nids/quickfinder/wiki")))
        self.iface.addPluginToMenu("&Quick Finder", self.helpAction)
                    
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Quick Finder", self.dockAction)
        self.iface.removePluginMenu("&Quick Finder", self.helpAction)
        self.iface.removeToolBarIcon(self.dockAction)
