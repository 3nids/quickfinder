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

from my_settings import MySettings


class AbstractFinder(QObject):

    name = ''  # to be defined in subclasses

    continue_search = False
    transform = None  # to be defined by subclasses

    # progress = pyqtSignal(QObject, int, int)  # total current

    result_found = pyqtSignal(QObject, str, str, QgsGeometry, int)
    limit_reached = pyqtSignal(QObject, str)
    finished = pyqtSignal(QObject)
    message = pyqtSignal(str, QgsMessageBar.MessageLevel)

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.settings = MySettings()

    def start(self, to_find, bbox=None):
        self.continue_search = True

    def stop(self):
        self.continue_search = False

    def activated(self):
        return self.settings.value(self.name)

    def close(self):
        pass

    def _finish(self):
        self.continue_search = False
        self.finished.emit(self)

    def is_running(self):
        return self.continue_search

    def reload(self):
        pass
