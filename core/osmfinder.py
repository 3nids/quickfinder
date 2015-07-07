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

import json

from qgis.core import QgsGeometry

from quickfinder.core.httpfinder import HttpFinder

class OsmFinder(HttpFinder):

    name = 'osm'

    def __init__(self, parent):
        HttpFinder.__init__(self, parent)

    def start(self, toFind, bbox=None):
        super(OsmFinder, self).start(toFind, bbox)

        url = self.settings.value('osmUrl')

        # The preferred area to find search results
        viewbox = '{},{},{},{}'.format(bbox.xMinimum(),
                                       bbox.yMaximum(),
                                       bbox.xMaximum(),
                                       bbox.yMinimum())

        params = {
            'q'            : toFind,
            'format'       : 'json',
            'polygon_text' : '1',
            'viewbox'      : viewbox,
            'limit'        : str(self.settings.value('totalLimit'))
        }
        # 'bounded' : '1'
        self._sendRequest(url, params)

    def loadData(self, data):
        for d in data:
            try:
                wkt = d['geotext']
            except KeyError:
                wkt = 'POINT(%s %s)' % (d['lon'], d['lat'])
            geometry = QgsGeometry.fromWkt(wkt)
            self.resultFound.emit(self,
                                  d['type'],
                                  d['display_name'],
                                  geometry,
                                  4326)
        self._finish()
