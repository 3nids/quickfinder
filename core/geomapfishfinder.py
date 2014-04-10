'''
Created on 24 mars 2014

@author: arnaud
'''

import urllib, urllib2, json, ogr

from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem, \
                      QgsCoordinateTransform
from qgis.gui import QgsMessageBar

from .abstractfinder import AbstractFinder
from .mysettings import MySettings

class GeomapfishFinder(AbstractFinder):

    name = 'GeoMapFish'
    asynchonous = True

    def __init__(self, parent):
        super(GeomapfishFinder, self).__init__(parent)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.replyFinished)

    def activated(self):
        return MySettings().value('geomapfish')

    def start(self, toFind, crs=None, bbox=None):
        super(GeomapfishFinder, self).start(toFind, crs, bbox)

        if self.asynchonous:
            url = QUrl(MySettings().value('geomapfish_url'))
            url.addQueryItem('query', toFind)
            url.addQueryItem('limit',
                             str(MySettings().value('geomapfish_limit')))
            url.addQueryItem('partitionlimit',
                             str(MySettings().value('geomapfish_partitionlimit')))

            request = QNetworkRequest(url)
            self.manager.get(request)

        else:
            url = MySettings().value('geomapfish_url')
            params = urllib.urlencode({
                        'query'          : toFind,
                        'limit'          :
                            str(MySettings().value('geomapfish_limit')),
                        'partitionlimit' :
                            str(MySettings().value('geomapfish_partitionlimit'))})
            response = json.load(urllib2.urlopen(url + '?' + params))
            self.loadData(response)

    def replyFinished(self, reply):
        data = json.loads(reply.readAll().data())
        self.loadData(data)

    def loadData(self, data):

        self.transform = None
        srv_crs_authid = MySettings().value('geomapfish_crs')
        srv_crs_authid = int(srv_crs_authid.replace('EPSG:', ''))
        if self.crs.authid() != srv_crs_authid:
            srv_crs = QgsCoordinateReferenceSystem()
            srv_crs.createFromSrid(srv_crs_authid)
            self.transform = QgsCoordinateTransform(srv_crs, self.crs)

        features = data['features']
        for f in features:

            json_geom = json.dumps(f['geometry'])
            ogr_geom = ogr.CreateGeometryFromJson(json_geom)
            wkt = ogr_geom.ExportToWkt()
            geometry = QgsGeometry.fromWkt(wkt)

            properties = f['properties']

            if not self._resultFound(properties['layer_name'],
                                     properties['label'],
                                     geometry):
                return

        self._finish()
