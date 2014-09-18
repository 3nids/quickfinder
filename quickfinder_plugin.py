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
from PyQt4.QtCore import Qt, QObject, QSettings, QCoreApplication, QTranslator, QUrl, pyqtSlot
from PyQt4.QtGui import QAction, QIcon, QColor, QDesktopServices, QMessageBox
from qgis.gui import QgsRubberBand, QgsMessageBar

from quickfinder.core.projectfinder import ProjectFinder, nDaysAgoIsoDate
from quickfinder.core.osmfinder import OsmFinder
from quickfinder.core.geomapfishfinder import GeomapfishFinder
from quickfinder.core.mysettings import MySettings
from quickfinder.gui.configurationdialog import ConfigurationDialog
from quickfinder.gui.refreshdialog import RefreshDialog
from quickfinder.gui.finderbox import FinderBox

import resources_rc


class quickFinder(QObject):

    name = u"&Quick Finder"
    actions = None
    toolbar = None
    finders = None

    loadingIcon = None

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface
        self.actions = {}
        self.finders = {}
        self.settings = MySettings()

        self._initFinders()

        self.iface.projectRead.connect(self._reloadFinders)
        self.iface.newProjectCreated.connect(self._reloadFinders)

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
                QUrl("http://3nids.github.io/quickfinder")))
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
        self.searchAction = QAction(QIcon(":/plugins/quickfinder/icons/magnifier13.svg"),
                                     self.tr("Search"),
                                     self.toolbar)
        self.stopAction = QAction(
            QIcon(":/plugins/quickfinder/icons/wrong2.svg"),
            self.tr("Cancel"),
            self.toolbar)
        self.finderBox = FinderBox(self.finders, self.iface, self.toolbar)
        self.finderBox.searchStarted.connect(self.searchStarted)
        self.finderBox.searchFinished.connect(self.searchFinished)
        self.finderBoxAction = self.toolbar.addWidget(self.finderBox)
        self.finderBoxAction.setVisible(True)
        self.searchAction.triggered.connect(self.finderBox.search)
        self.toolbar.addAction(self.searchAction)
        self.stopAction.setVisible(False)
        self.stopAction.triggered.connect(self.finderBox.stop)
        self.toolbar.addAction(self.stopAction)
        self.toolbar.setVisible(True)

    def _initFinders(self):
        self.finders = {
            'geomapfish': GeomapfishFinder(self),
            'osm': OsmFinder(self),
            'project': ProjectFinder(self)
        }
        for key in self.finders.keys():
            self.finders[key].message.connect(self.displayMessage)
        self.refreshProject()

    def _reloadFinders(self):
        for key in self.finders.keys():
            self.finders[key].reload()
        self.refreshProject()

    @pyqtSlot(str, QgsMessageBar.MessageLevel)
    def displayMessage(self, message, level):
        self.iface.messageBar().pushMessage("QuickFinder", message, level)

    def showSettings(self):
        if ConfigurationDialog().exec_():
            self._initFinders()

    def searchStarted(self):
        self.searchAction.setVisible(False)
        self.stopAction.setVisible(True)

    def searchFinished(self):
        self.searchAction.setVisible(True)
        self.stopAction.setVisible(False)

    def refreshProject(self):
        if not self.finders['project'].activated:
            return
        if not self.settings.value("refreshAuto"):
            return
        nDays = self.settings.value("refreshDelay")
        # do not ask more ofen than 3 days
        askLimit = min(3, nDays)
        recentlyAsked = self.settings.value("refreshLastAsked") >= nDaysAgoIsoDate(askLimit)
        if recentlyAsked:
            return
        threshDate = nDaysAgoIsoDate(nDays)
        uptodate = True
        for search in self.finders['project'].searches.values():
            if search.dateEvaluated <= threshDate:
                uptodate = False
                break
        if uptodate:
            return
        self.settings.setValue("refreshLastAsked", nDaysAgoIsoDate(0))
        ret = QMessageBox(QMessageBox.Warning,
                          "Quick Finder",
                          QCoreApplication.translate("Auto Refresh", "Some searches are outdated. Do you want to refresh them ?"),
                          QMessageBox.Cancel | QMessageBox.Yes).exec_()
        if ret == QMessageBox.Yes:
            RefreshDialog(self.finders['project']).exec_()



