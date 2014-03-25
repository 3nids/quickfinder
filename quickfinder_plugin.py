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

from PyQt4.QtCore import Qt, QObject, QSettings, QCoreApplication, \
                         QTranslator, QUrl, QEventLoop
from PyQt4.QtGui import QAction, QIcon, \
                        QTreeView, QSizePolicy, QDesktopServices

from quickfinder.core.resultmodel import ResultModel
from quickfinder.core.projectfinder import ProjectFinder
from quickfinder.core.osmfinder import OsmFinder
from quickfinder.gui.finderbox import FinderBox
from quickfinder.gui.mysettingsdialog import MySettingsDialog

import resources_rc


class quickFinder(QObject):

    name = u"&Quick Finder"
    actions = {}
    toolbar = None
    finders = {}
    running = False

    def __init__(self, iface):
        """Constructor for the plugin.

        :param iface: A QGisAppInterface instance we use to access QGIS via.
        :type iface: QgsAppInterface
        """
        super(quickFinder, self).__init__()

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'easysearch_{}.qm'.format(locale))

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
        self._initFinders()

        '''
        self.iface.projectRead.connect(self.searchText_placeholderTextUpdate)
        self.iface.newProjectCreated.connect(self.searchText_placeholderTextUpdate)
        '''

    def unload(self):
        # Remove the plugin menu item and icon
        for action in self.actions.values():
            self.iface.removePluginMenu(self.name, action)

        if self.toolbar:
            # self.toolbar.deleteLater()
            del self.toolbar
            # self.toolbar = None

        '''
        self.iface.projectRead.disconnect(self.searchText_placeholderTextUpdate)
        self.iface.newProjectCreated.disconnect(self.searchText_placeholderTextUpdate)
        '''

    def _initToolbar(self):
        """setup the plugin toolbar."""
        self.toolbar = self.iface.addToolBar(self.name)
        self.toolbar.setObjectName('mQuickFinderToolBar')

        self.finderBox = FinderBox(self.toolbar)
        self.finderBox.setMinimumHeight(27)
        self.finderBox.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Fixed)

        self.finderBoxAction = self.toolbar.addWidget(self.finderBox)
        self.finderBoxAction.setVisible(True);
        self.finderBox.lineEdit().returnPressed.connect(self.search)

        self.resultModel = ResultModel(self.finderBox)
        self.finderBox.setModel(self.resultModel)

        self.resultView = QTreeView()
        self.resultView.setHeaderHidden(True)
        self.resultView.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded);
        self.resultView.setFixedHeight(300);
        self.finderBox.setView(self.resultView)

        self.searchIcon = QIcon(":/plugins/quickfinder/icons/magnifier13.svg")
        self.stopIcon = QIcon(":/plugins/quickfinder/icons/wrong2.svg")

        self.searchAction = QAction(
            self.searchIcon,
            self.tr("Search"),
            self.toolbar)
        self.searchAction.triggered.connect(self.onSearchAction)
        self.toolbar.addAction(self.searchAction)

        self.stopAction = QAction(
            self.stopIcon,
            self.tr("Cancel"),
            self.toolbar)
        self.stopAction.setVisible(False)
        self.stopAction.triggered.connect(self.stop)
        self.toolbar.addAction(self.stopAction)

        self.toolbar.setVisible(True)

    def _initFinders(self):
        self.finders['project'] = ProjectFinder()
        self.finders['osm'] = OsmFinder()

        for finder in self.finders.values():
            finder.resultFound.connect(self.resultFound)
            finder.message.connect(self.displayMessage)
            finder.finished.connect(self.searchFinished)

    def showSettings(self):
        MySettingsDialog().exec_()

    def onSearchAction(self):
        if self.running:
            self.stop()
        else:
            self.search()

    def stop(self):
        self.running = False
        # self.searchAction.setIcon(self.searchIcon)
        '''
        self.toolbar.widgetForAction(self.stopAction).setVisible(False)
        self.toolbar.widgetForAction(self.searchAction).setVisible(True)
        '''
        self.stopAction.setVisible(False)
        self.searchAction.setVisible(True)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        for finder in self.finders.values():
            if finder.isRunning():
                finder.stop()

        # self.progressWidget.hide()

    def search(self):
        self.running = True
        # self.searchAction.setIcon(self.stopIcon)
        # self.toolbar.widgetForAction(self.searchAction).setIcon(self.stopIcon)
        '''
        self.toolbar.widgetForAction(self.searchAction).setVisible(False)
        self.toolbar.widgetForAction(self.stopAction).setVisible(True)
        '''
        self.searchAction.setVisible(False)
        self.stopAction.setVisible(True)
        # QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        QCoreApplication.processEvents()

        toFind = self.finderBox.currentText()

        self.stop()
        self.resultModel.clearResults()

        self.finderBox.showPopup()

        '''
        # show progress bar
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(self.layer.pendingFeatureCount())
        self.progressBar.setValue(0)
        self.progressWidget.show()
        '''

        '''
        for finder in self.finders.values():
            finder.start(toFind)
        '''
        self.finders['project'].start(toFind)

    def resultFound(self, category, layername, value, geometry):
        self.resultModel.addResult(category, layername, value, geometry)
        self.resultView.expandAll()

    def displayMessage(self, message, level):
        self.iface.messageBar().pushMessage("Quick Finder", message, level, 3)

    def searchFinished(self):
        for finder in self.finders.values:
            if finder.isRunning():
                return
        self.stop()
