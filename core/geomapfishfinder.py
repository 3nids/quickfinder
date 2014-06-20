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

import urllib, urllib2, json, ogr

from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest


from quickfinder.core.abstractfinder import AbstractFinder

class GeomapfishFinder(AbstractFinder):

    name = 'geomapfish'
    asynchonous = True

    def __init__(self, parent):
        super(GeomapfishFinder, self).__init__(parent)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.replyFinished)

    def start(self, toFind, bbox=None):
        super(GeomapfishFinder, self).start(toFind, bbox)

        if self.asynchonous:
            url = QUrl(self.settings.value('geomapfishUrl'))
            url.addQueryItem('query', toFind)
            url.addQueryItem('limit', str(self.settings.value('totalLimit')))
            url.addQueryItem('partitionlimit', str(self.settings.value('categoryLimit')))

            request = QNetworkRequest(url)
            self.manager.get(request)

        else:
            url = self.settings.value('geomapfishUrl')
            params = urllib.urlencode({
                        'query'          : toFind,
                        'limit'          : str(self.settings.value('totalLimit')),
                        'partitionlimit' : str(self.settings.value('categoryLimit'))})
            response = json.load(urllib2.urlopen(url + '?' + params))
            self.loadData(response)

    def replyFinished(self, reply):
        data = json.loads(reply.readAll().data())
        self.loadData(data)

    def loadData(self, data):
        srv_crs_authid = self.settings.value('geomapfishCrs')
        srv_crs_authid = int(srv_crs_authid.replace('EPSG:', ''))
        features = data['features']
        for f in features:
            json_geom = json.dumps(f['geometry'])
            ogr_geom = ogr.CreateGeometryFromJson(json_geom)
            wkt = ogr_geom.ExportToWkt()
            geometry = QgsGeometry.fromWkt(wkt)
            properties = f['properties']
            self.resultFound.emit(self,
                                  properties['layer_name'],
                                  properties['label'],
                                  geometry,
                                  srv_crs_authid)
        self._finish()
