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

import os.path
from collections import OrderedDict

from PyQt4.QtCore import Qt, QObject, QSettings, QCoreApplication, \
                         QTranslator, QUrl
from PyQt4.QtGui import QAction, QIcon, QColor, \
                        QDesktopServices

from qgis.gui import QgsRubberBand


from quickfinder.core.localfinder import LocalFinder
from quickfinder.core.osmfinder import OsmFinder
from quickfinder.core.geomapfishfinder import GeomapfishFinder
from quickfinder.gui.configurationdialog import ConfigurationDialog

from quickfinder.gui.finderbox import FinderBox

import resources_rc


class quickFinder(QObject):

    name = u"&Quick Finder"
    actions = None
    toolbar = None
    finders = None

    loadingIcon = None

    def __init__(self, iface):
        """Constructor for the plugin.

        :param iface: A QGisAppInterface instance we use to access QGIS via.
        :type iface: QgsAppInterface
        """
        super(quickFinder, self).__init__()

        # Save reference to the QGIS interface
        self.iface = iface

        self.actions = {}
        self.finders = {}

        self._initFinders()

        # translation environment
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'quickfinder_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        self.actions['showSettings'] = QAction(
            QIcon(":/plugins/quickfinder/icons/settings.svg"),
            self.tr(u"&Settings"),
            self.iface.mainWindow())
        self.actions['showSettings'].triggered.connect(self.showSettings)
        self.iface.addPluginToMenu(self.name, self.actions['showSettings'])

        self.actions['help'] = QAction(
            QIcon(":/plugins/quickfinder/icons/help.svg"),
            self.tr("Help"),
            self.iface.mainWindow())
        self.actions['help'].triggered.connect(
            lambda: QDesktopServices().openUrl(
                QUrl("https://github.com/3nids/quickfinder/wiki")))
        self.iface.addPluginToMenu(self.name, self.actions['help'])

        self._initToolbar()

        self.rubber = QgsRubberBand(self.iface.mapCanvas())
        self.rubber.setColor(QColor(255, 255, 50, 200))
        self.rubber.setIcon(self.rubber.ICON_CIRCLE)
        self.rubber.setIconSize(15)
        self.rubber.setWidth(4)
        self.rubber.setBrushStyle(Qt.NoBrush)

    def unload(self):
        """Remove the plugin menu item and icon """
        for action in self.actions.itervalues():
            self.iface.removePluginMenu(self.name, action)

        if self.toolbar:
            del self.toolbar

        if self.rubber:
            self.iface.mapCanvas().scene().removeItem(self.rubber)
            del self.rubber

    def _initToolbar(self):
        """setup the plugin toolbar."""
        self.toolbar = self.iface.addToolBar(self.name)
        self.toolbar.setObjectName('mQuickFinderToolBar')

        self.searchAction = QAction( QIcon(":/plugins/quickfinder/icons/magnifier13.svg"),
                                     self.tr("Search"),
                                     self.toolbar)
        self.stopAction = QAction(
            QIcon(":/plugins/quickfinder/icons/wrong2.svg"),
            self.tr("Cancel"),
            self.toolbar)

        self.finderBox = FinderBox(self.finders, self.iface, self.toolbar)
        self.finderBox.searchStarted.connect(self.enableSearch)
        self.finderBox.searchFinished.connect(self.disableSearch)

        self.finderBoxAction = self.toolbar.addWidget(self.finderBox)
        self.finderBoxAction.setVisible(True)


        self.searchAction.triggered.connect(self.finderBox.search)
        self.toolbar.addAction(self.searchAction)


        self.stopAction.setVisible(False)
        self.stopAction.triggered.connect(self.finderBox.stop)
        self.toolbar.addAction(self.stopAction)

        self.toolbar.setVisible(True)

    def _initFinders(self):
        """Create finders and connect signals"""
        self.finders = OrderedDict()
        self.finders['geomapfish'] = GeomapfishFinder(self)
        self.finders['osm'] = OsmFinder(self)
        self.finders['local'] = LocalFinder(self)

    def showSettings(self):
        if ConfigurationDialog().exec_():
            self.finders['local'].reload()

    def enableSearch(self):
        self.searchAction.setVisible(True)
        self.stopAction.setVisible(False)

    def disableSearch(self):
        self.searchAction.setVisible(False)
        self.stopAction.setVisible(True)


