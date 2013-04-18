"""
Quick Finder
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

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
                        lambda: QDesktopServices.openUrl(QUrl("https://github.com/3nids/quickfinder/wiki")))
        self.iface.addPluginToMenu("&Quick Finder", self.helpAction)
                    
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Quick Finder", self.dockAction)
        self.iface.removePluginMenu("&Quick Finder", self.helpAction)
        self.iface.removeToolBarIcon(self.dockAction)
