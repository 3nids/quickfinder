
#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2017 Pirmin Kalberer, Sourcepole AG
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

from PyQt4.QtCore import pyqtSignal, QObject
from qgis.core import QgsMapLayerRegistry


class PostgisSearch(QObject):

    changed = pyqtSignal()

    @property
    def searchId(self): return self._searchId
    @property
    def searchName(self): return self._searchName
    @property
    def expression(self): return self._expression
    @property
    def priority(self): return self._priority
    @property
    def srid(self): return self._srid
    @property
    def project(self): return self._project

    def __init__(self, searchId, searchName, expression, priority, srid,
                 project):
        QObject.__init__(self)

        self._searchId = searchId
        self._searchName = searchName
        self._expression = expression
        self._priority = priority
        self._srid = srid
        self._project = project

    def edit(self, searchName, expression, priority, srid,
                 project):
        self._searchName = searchName
        self._expression = expression
        self._priority = priority
        self._srid = srid
        self._project = project

        self.changed.emit()
