'''
Created on 24 mars 2014

@author: arnaud
'''

import urllib, urllib2, json

from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

from qgis.core import QgsGeometry

from quickfinder.core.abstractfinder import AbstractFinder

class OsmFinder(AbstractFinder):

    name = 'osm'
    asynchonous = True

    def __init__(self, parent):
        super(OsmFinder, self).__init__(parent)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.replyFinished)

    def start(self, toFind, bbox=None):
        super(OsmFinder, self).start(toFind, bbox)

        # The preferred area to find search results
        viewbox = '{},{},{},{}'.format(bbox.xMinimum(),
                                       bbox.yMaximum(),
                                       bbox.xMaximum(),
                                       bbox.yMinimum())

        if self.asynchonous:
            url = QUrl(self.settings.value('osmUrl'))
            url.addQueryItem('q', toFind.encode('utf-8'))
            url.addQueryItem('format', 'json')
            url.addQueryItem('polygon_text', '1')
            url.addQueryItem('limit', str(self.settings.value('totalLimit')))
            url.addQueryItem('viewbox', viewbox)
            # url.addQueryItem('bounded', '1')

            request = QNetworkRequest(url)
            self.manager.get(request)

        else:
            url = self.settings.value('osmUrl')
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
