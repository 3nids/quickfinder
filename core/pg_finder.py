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

from PyQt4.QtCore import QObject, pyqtSignal

from qgis.core import QgsGeometry, QgsCredentials
from qgis.gui import QgsMessageBar

from my_settings import MySettings

import psycopg2
import binascii

from processing.tools.postgis import uri_from_name, DbError


from .abstract_finder import AbstractFinder


class PgFinder(AbstractFinder):

    name = 'postgres'

    def __init__(self, parent):
        super(PgFinder, self).__init__(parent)

    def start(self, to_find, bbox=None):
        super(PgFinder, self).start(to_find, bbox)
        # TODO: GUI + support for multiple connections
        dbConnectionName = self.settings.value('pgConnection')
        try:
            connectionUri = uri_from_name(dbConnectionName)
        except DbError as err:
            self.message.emit(unicode(err), QgsMessageBar.WARNING)
            self._finish()
            return
        self.cur = self.connectToUri(connectionUri)
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
        query = """SELECT r1_nummer::text,ST_AsBinary(wkb_geometry)::geometry
            FROM av.li_liegenschaft_a
            WHERE r1_nummer LIKE %s
            LIMIT %s"""
        self.cur.execute(query, (to_find, catLimit))
        for row in self.cur.fetchall():
            content, wkb_geom = row
            geometry = QgsGeometry()
            geometry.fromWkb(binascii.a2b_hex(wkb_geom))
            self.result_found.emit(self,
                                   'li_liegenschaft_a',
                                   content,
                                   geometry,
                                   21781)
            #if sum(catFound.values()) >= totalLimit:
            #    break
