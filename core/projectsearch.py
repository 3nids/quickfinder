
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

from PyQt4.QtCore import pyqtSignal, QObject
from qgis.core import QgsMapLayerRegistry


class ProjectSearch(QObject):

    changed = pyqtSignal()

    @property
    def searchId(self): return self._searchId
    @property
    def searchName(self): return self._searchName
    @property
    def layerid(self): return self._layerid
    @property
    def layerName(self): return self._layerName
    @property
    def expression(self): return self._expression
    @property
    def priority(self): return self._priority
    @property
    def srid(self): return self._srid
    @property
    def dateEvaluated(self): return self._dateEvaluated
    @dateEvaluated.setter
    def dateEvaluated(self, value):
        self._dateEvaluated = value
        self._status = "evaluated"
        self.changed.emit()

    def __init__(self, searchId, searchName, layerid, layerName, expression, priority, srid, dateEvaluated=None):
        QObject.__init__(self)

        self._searchId = searchId
        self._searchName = searchName
        self._layerid = layerid
        self._layerName = layerName
        self._expression = expression
        self._priority = priority
        self._srid = srid
        self._dateEvaluated = dateEvaluated

        if dateEvaluated is None:
            self._status = "not_evaluated"
        else:
            self._status = 'evaluated'

    def layer(self):
        return QgsMapLayerRegistry.instance().mapLayer(self._layerid)


    def edit(self, searchName, layerid, layerName, expression, priority, srid):
        self._searchName = searchName
        self._layerid = layerid
        self._layerName = layerName
        self._expression = expression
        self._priority = priority
        self._srid = srid
        self._dateEvaluated = None
        self._status = "not_evaluated"
        self.changed.emit()


