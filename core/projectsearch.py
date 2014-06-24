
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

from qgis.core import QgsMapLayerRegistry



class ProjectSearch():
    def __init__(self, searchId, searchName, layerid, layerName, expression, priority, srid, dateEvaluated=None):
        self.searchId = searchId
        self.searchName = searchName
        self.layerid = layerid
        self.layerName = layerName
        self.expression = expression
        self.priority = priority
        self.srid = srid
        self.dateEvaluated = dateEvaluated

        self.layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not self.layer:
            self.status = "layer_deleted"
        elif dateEvaluated is None:
            self.status = "not_evaluated"
        else:
            self.status = 'evaluated'
