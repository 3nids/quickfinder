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

from PyQt4.QtCore import Qt, QObject, pyqtSlot, QSettings, QCoreApplication, \
                         QTranslator, QUrl, QEventLoop
from PyQt4.QtGui import QAction, QIcon, QColor, \
                        QComboBox, QTreeView, QSizePolicy, \
                        QDesktopServices

from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, \
                        QGis
from qgis.gui import QgsRubberBand


from quickfinder.core.mysettings import MySettings
from quickfinder.core.resultmodel import ResultModel, ResultItem
from quickfinder.core.projectfinder import ProjectFinder
from quickfinder.core.osmfinder import OsmFinder
# from quickfinder.gui.finderbox import FinderBox
from quickfinder.gui.mysettingsdialog import MySettingsDialog

import resources_rc


class quickFinder(QObject):

    name = u"&Quick Finder"
    actions = None
    toolbar = None
    finders = None
    running = False

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

        self.rubber = QgsRubberBand(self.iface.mapCanvas())
        self.rubber.setColor(QColor(255, 255, 50, 200))
        self.rubber.setIcon(self.rubber.ICON_CIRCLE)
        self.rubber.setIconSize(15)
        self.rubber.setWidth(4)
        self.rubber.setBrushStyle(Qt.NoBrush)

        '''
        self.iface.projectRead.connect(self.searchText_placeholderTextUpdate)
        self.iface.newProjectCreated.connect(self.searchText_placeholderTextUpdate)
        '''

    def unload(self):
        # Remove the plugin menu item and icon
        for action in self.actions.itervalues():
            self.iface.removePluginMenu(self.name, action)

        if self.toolbar:
            del self.toolbar

        if self.rubber:
            self.iface.mapCanvas().scene().removeItem(self.rubber)
            del self.rubber

        '''
        self.iface.projectRead.disconnect(self.searchText_placeholderTextUpdate)
        self.iface.newProjectCreated.disconnect(self.searchText_placeholderTextUpdate)
        '''

    def _initToolbar(self):
        """setup the plugin toolbar."""
        self.toolbar = self.iface.addToolBar(self.name)
        self.toolbar.setObjectName('mQuickFinderToolBar')

        self.finderBox = QComboBox(self.toolbar)
        self.finderBox.setEditable(True)
        self.finderBox.setInsertPolicy(QComboBox.InsertAtTop)
        self.finderBox.setMinimumHeight(27)
        self.finderBox.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Fixed)

        self.finderBoxAction = self.toolbar.addWidget(self.finderBox)
        self.finderBoxAction.setVisible(True)
        self.finderBox.insertSeparator(0)
        self.finderBox.lineEdit().returnPressed.connect(self.search)

        self.resultModel = ResultModel(self.finderBox)
        self.finderBox.setModel(self.resultModel)

        self.resultView = QTreeView()
        self.resultView.setHeaderHidden(True)
        self.resultView.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded);
        self.resultView.setMinimumHeight(300);
        self.resultView.clicked.connect(self.itemClicked)
        self.resultView.activated.connect(self.itemActivated)
        self.finderBox.setView(self.resultView)

        self.searchAction = QAction(
            QIcon(":/plugins/quickfinder/icons/magnifier13.svg"),
            self.tr("Search"),
            self.toolbar)
        self.searchAction.triggered.connect(self.search)
        self.toolbar.addAction(self.searchAction)

        self.stopAction = QAction(
            QIcon(":/plugins/quickfinder/icons/wrong2.svg"),
            self.tr("Cancel"),
            self.toolbar)
        self.stopAction.setVisible(False)
        self.stopAction.triggered.connect(self.stop)
        self.toolbar.addAction(self.stopAction)

        self.toolbar.setVisible(True)

    def _initFinders(self):
        self.finders['project'] = ProjectFinder(self)
        # self.finders['osm'] = OsmFinder(self)

        for finder in self.finders.itervalues():
            finder.resultFound.connect(self.resultFound)
            finder.limitReached.connect(self.limitReached)
            finder.finished.connect(self.finished)
            finder.message.connect(self.message)

    def showSettings(self):
        MySettingsDialog().exec_()

    def search(self):
        if self.running:
            return

        # toFind = self.finderBox.currentText()
        toFind = self.finderBox.lineEdit().text()
        if not toFind:
            return

        print self.__class__.__name__, 'search', toFind

        self.running = True

        self.searchAction.setVisible(False)
        self.stopAction.setVisible(True)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        self.resultModel.clearResults()
        self.resultModel.truncateHistory(MySettings().value("historyLength"))

        self.finderBox.showPopup()

        '''
        # show progress bar
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(self.layer.pendingFeatureCount())
        self.progressBar.setValue(0)
        self.progressWidget.show()
        '''

        for finder in self.finders.itervalues():
            finder.start(toFind)

    def stop(self):
        print self.__class__.__name__, 'stop'
        for finder in self.finders.itervalues():
            if finder.isRunning():
                finder.stop()

    def resultFound(self, finder, layername, value, geometry):
        print self.__class__.__name__, 'resultFound', finder.name, layername, value
        self.resultModel.addResult(finder.name, layername, value, geometry)
        self.resultView.expandAll()

    def limitReached(self, finder, layername):
        print self.__class__.__name__, 'limitReached', finder.name, layername
        self.resultModel.addEllipsys(finder.name, layername)

    def finished(self, finder):
        # wait for all running finders
        for finder in self.finders.itervalues():
            if finder.isRunning():
                return

        print self.__class__.__name__, 'searchFinished'
        self.running = False

        # self.progressWidget.hide()
        self.stopAction.setVisible(False)
        self.searchAction.setVisible(True)
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def message(self, finder, message, level):
        self.iface.messageBar().pushMessage("Quick Finder", message, level, 3)

    def itemActivated(self, index):
        item = self.resultModel.itemFromIndex(index)
        print self.__class__.__name__, 'itemActivated', item
        if isinstance(item, ResultItem):
            self.showGeometry(item.geometry)

    def itemClicked(self, index):
        item = self.resultModel.itemFromIndex(index)
        print self.__class__.__name__, 'itemClicked', item
        if isinstance(item, ResultItem):
            self.showGeometry(item.geometry)

    def showGeometry(self, geometry):
        print self.__class__.__name__, 'showGeometry'

        rect = geometry.boundingBox()
        rect.scale(1.5)
        self.iface.mapCanvas().setExtent(rect)
        self.iface.mapCanvas().refresh()

        self.rubber.reset(geometry.type())
        self.rubber.setToGeometry(geometry, None)
