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
from osgeo import ogr
from PyQt4.QtCore import QByteArray
from qgis.core import QgsGeometry
from http_finder import HttpFinder


class GeomapfishFinder(HttpFinder):

    name = 'geomapfish'

    def __init__(self, parent):
        HttpFinder.__init__(self, parent)

    def start(self, to_find, crs=None, bbox=None):
        super(GeomapfishFinder, self).start(to_find, bbox)
        url = self.settings.value('geomapfishUrl')
        params = {
            'query': to_find,
            'limit': str(self.settings.value('totalLimit')),
            'partitionlimit': str(self.settings.value('categoryLimit'))
        }
        headers = {}

        if self.settings.value('geomapfishUser') != '':
            user = self.settings.value('geomapfishUser')
            password = self.settings.value('geomapfishPass')
            auth_data = "{}:{}".format(user, password)
            b64 = QByteArray(auth_data).toBase64()
            headers['Authorization'] = 'Basic ' + b64
        self._sendRequest(url, params, headers)

    def load_data(self, data):
        srv_crs_authid = self.settings.value('geomapfishCrs')
        srv_crs_authid = int(srv_crs_authid.replace('EPSG:', ''))
        features = data['features']
        for f in features:
            json_geom = json.dumps(f['geometry'])
            ogr_geom = ogr.CreateGeometryFromJson(json_geom)
            wkt = ogr_geom.ExportToWkt()
            geometry = QgsGeometry.fromWkt(wkt)
            properties = f['properties']
            if geometry is None:
                continue
            self.result_found.emit(self,
                                   properties['layer_name'],
                                   properties['label'],
                                   geometry,
                                   srv_crs_authid)
        self._finish()
