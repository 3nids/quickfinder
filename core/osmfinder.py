'''
Created on 24 mars 2014

@author: arnaud
'''

import urllib, urllib2, json

from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, \
                            QNetworkRequest

from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem, \
                      QgsCoordinateTransform
from qgis.gui import QgsMessageBar

from .basefinder import BaseFinder
from .mysettings import MySettings

class OsmFinder(BaseFinder):

    name = 'OpenStreetMap'
    asynchonous = True

    def __init__(self, parent):
        super(OsmFinder, self).__init__(parent)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.replyFinished)

    def start(self, toFind, crs=None, bbox=None):
        super(OsmFinder, self).start(toFind, crs, bbox)

        # The preferred area to find search results
        viewbox = '{},{},{},{}'.format(bbox.xMinimum(),
                                       bbox.yMaximum(),
                                       bbox.xMaximum(),
                                       bbox.yMinimum())

        if self.asynchonous:
            url = QUrl(MySettings().value('osm_url'))
            url.addQueryItem('q', toFind.encode('utf-8'))
            url.addQueryItem('format', 'json')
            url.addQueryItem('polygon_text', '1')
            url.addQueryItem('limit', str(MySettings().value('osm_limit')))
            url.addQueryItem('viewbox', viewbox)
            # url.addQueryItem('bounded', '1')

            request = QNetworkRequest(url)
            self.manager.get(request)

        else:
            url = MySettings().value('osm_url')
            params = urllib.urlencode({
                        'q'             : toFind.encode('utf-8'),
                        'format'        : 'json',
                        'polygon_text'  : '1',
                        'viewbox'       : viewbox})
            response = json.load(urllib2.urlopen(url + '?' + params))
            self.loadData(response)

    def replyFinished(self, reply):
        data = json.loads(reply.readAll().data())
        self.loadData(data)

    def loadData(self, data):

        self.transform = None
        if self.crs.srsid() != 4326:
            wgs84 = QgsCoordinateReferenceSystem()
            wgs84.createFromSrid(4326)
            self.transform = QgsCoordinateTransform(wgs84, self.crs)

        for d in data:

            try:
                wkt = d['geotext']
            except KeyError:
                wkt = 'POINT(%s %s)' % (d['lon'], d['lat'])
            geometry = QgsGeometry.fromWkt(wkt)

            if not self._resultFound(d['type'],
                                     d['display_name'],
                                     geometry):
                return

        self._finish()
