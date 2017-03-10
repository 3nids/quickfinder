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

from PyQt4.QtCore import QObject, QSettings

from qgis.core import QgsGeometry, QgsCredentials
from qgis.gui import QgsMessageBar

from my_settings import MySettings

import psycopg2
import binascii

from postgis_search import PostgisSearch
from .abstract_finder import AbstractFinder

try:
    from processing.tools.postgis import uri_from_name, DbError
except ImportError:
    # Older processing versions don't have this helper
    # PostGIS finder won't work.
    pass  # Don't prevent quickfinder plugin from loading.


class PostgisFinder(AbstractFinder):

    name = 'postgis'

    @property
    def searches(self): return self._searches

    def __init__(self, parent):
        super(PostgisFinder, self).__init__(parent)
        self._searches = self.readSearches()

    def start(self, to_find, bbox=None):
        super(PostgisFinder, self).start(to_find, bbox)
        dbConnectionName = self.settings.value('postgisConnection')
        self.cur = None
        if dbConnectionName:
            try:
                connectionUri = uri_from_name(dbConnectionName)
                self.cur = self.connectToUri(connectionUri)
            except DbError as err:
                self.message.emit(unicode(err), QgsMessageBar.WARNING)
            if self.cur:
                self.find(to_find)
        self._finish()

    def connectToUri(self, uri):
        """Create a connection from a uri and return a cursor of it."""
        conninfo = uri.connectionInfo()
        conn = None
        cur = None
        ok = False
        while not conn:
            try:
                conn = psycopg2.connect(uri.connectionInfo())
                cur = conn.cursor()
            except psycopg2.OperationalError as e:
                (ok, user, passwd) = QgsCredentials.instance().get(
                    conninfo, uri.username(), uri.password())
                if not ok:
                    break

        if not conn:
            self.message.emit(
                "Could not connect to PostgreSQL database",
                QgsMessageBar.WARNING)

        if ok:
            QgsCredentials.instance().put(conninfo, user, passwd)

        return cur

    def find(self, to_find):
        catLimit = self.settings.value("categoryLimit")
        totalLimit = self.settings.value("totalLimit")
        hasProjectSearches = len(self.settings.value("postgisSearches"))
        catFound = {}
        self._searches = self.readSearches()
        for searchId, search in self._searches.iteritems():
            if (not hasProjectSearches or
                    searchId in self.settings.value("postgisSearches")):
                # Expression example:
                # SELECT textfield, ST_AsBinary(wkb_geometry)::geometry
                #   FROM searchtable
                #   WHERE textfield LIKE %(search)s
                #   LIMIT %(limit)s
                self.cur.execute(search.expression,
                                 {'search': to_find, 'limit': catLimit})
                for row in self.cur.fetchall():
                    if searchId in catFound:
                        if catFound[searchId] >= catLimit:
                            continue
                        catFound[searchId] += 1
                    else:
                        catFound[searchId] = 1
                    content, wkb_geom = row
                    geometry = QgsGeometry()
                    geometry.fromWkb(binascii.a2b_hex(wkb_geom))
                    self.result_found.emit(self,
                                           search.searchName,
                                           content,
                                           geometry,
                                           search.srid)
                    if sum(catFound.values()) >= totalLimit:
                        break

    def searchSetting(self, searchId, name):
        return "/plugins/%s/postgis_search/%s/%s" % (
            self.settings.plugin_name, searchId, name)

    def readSearches(self):
        searches = {}
        settings = QSettings()
        settings.beginGroup(
            "/plugins/%s/postgis_search" % self.settings.plugin_name)
        for searchId in settings.childGroups():
            settings.beginGroup(searchId)
            searchName = settings.value('searchName')
            expression = settings.value('expression')
            priority = settings.value('priority', type=int)
            srid = settings.value('srid')
            project = searchId in self.settings.value("postgisSearches")
            searches[searchId] = PostgisSearch(
                searchId, searchName, expression, priority, srid, project)
            settings.endGroup()
        settings.endGroup()
        return searches

    def deleteSearch(self, searchId):
        settings = QSettings()
        settings.remove("/plugins/%s/postgis_search/%s" % (
            self.settings.plugin_name, searchId))
        return True

    def recordSearch(self, postgisSearch):
        searchId = postgisSearch.searchId

        # always remove existing search with same id
        self.deleteSearch(searchId)

        settings = QSettings()
        settings.setValue(self.searchSetting(searchId, 'searchName'),
                          postgisSearch.searchName)
        settings.setValue(self.searchSetting(searchId, 'expression'),
                          postgisSearch.expression)
        settings.setValue(self.searchSetting(searchId, 'priority'),
                          postgisSearch.priority)
        settings.setValue(self.searchSetting(searchId, 'srid'),
                          postgisSearch.srid)

        # Project
        ids = self.settings.value("postgisSearches")
        if searchId not in ids:
            ids.append(searchId)
            self.settings.setValue("postgisSearches", ids)

        return True, ""
