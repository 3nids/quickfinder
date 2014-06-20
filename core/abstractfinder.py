#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2014 Denis Rouzaud, Arnaud Morvan
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

from PyQt4.QtCore import QObject, pyqtSignal

from qgis.core import QgsGeometry
from qgis.gui import QgsMessageBar

from quickfinder.core.mysettings import MySettings


class AbstractFinder(QObject):

    name = ''  # to be defined in subclasses

    crs = None
    continueSearch = False
    transform = None  # to be defined by subclasses

    progress = pyqtSignal(QObject, int, int)  # total current
    resultFound = pyqtSignal(QObject, str, str, QgsGeometry)
    limitReached = pyqtSignal(QObject, str)
    finished = pyqtSignal(QObject)
    message = pyqtSignal(QObject, str, QgsMessageBar.MessageLevel)

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.settings = MySettings()

    def start(self, toFind, crs=None, bbox=None):
        self.crs = crs
        self.continueSearch = True

    def stop(self):
        self.continueSearch = False

    def activated(self):
        return MySettings().value(self.name)

    def _resultFound(self, layername, value, geometry):
        geometry = self._transform(geometry)
        if not geometry:
            self._finish()
            return False
        self.resultFound.emit(self, layername, value, geometry)
        return True

    def _transform(self, geometry):
        if self.transform:
            try:
                geometry.transform(self.transform)
            except:
                self.message.emit(self,
                                  'CRS transformation error!',
                                  QgsMessageBar.CRITICAL)
                self._finish()
                return
        return geometry

    def _finish(self):
        self.continueSearch = False
        self.finished.emit(self)

    def isRunning(self):
        return self.continueSearch
