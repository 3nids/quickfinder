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

import sqlite3
import binascii
from datetime import date, datetime, timedelta

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # for Python < 2.7

from PyQt4.QtCore import pyqtSignal, QCoreApplication
from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest, QgsExpression, QgsGeometry, QgsCoordinateReferenceSystem
from qgis.gui import QgsMessageBar
from quickfinder.core.projectsearch import ProjectSearch
from quickfinder.core.abstractfinder import AbstractFinder


def createFTSfile(filepath):
    conn = sqlite3.connect(filepath)

    sql = "CREATE TABLE quickfinder_info (key text,value text);"
    sql += "INSERT INTO quickfinder_info (key,value) VALUES ('scope','quickfinder');"
    sql += "INSERT INTO quickfinder_info (key,value) VALUES ('db_version','1.0');"
    sql += "CREATE TABLE quickfinder_toc (search_id text, search_name text, layer_id text, layer_name text, expression text, priority integer, srid text, date_evaluated text);"
    sql_unicode61 = sql + "CREATE VIRTUAL TABLE quickfinder_data USING fts4 (tokenize=unicode61 \"remove_diacritics=1\", search_id, content, x real, y real, wkb_geom text);"
    sql += "CREATE VIRTUAL TABLE quickfinder_data USING fts4 (search_id, content, x real, y real, wkb_geom text);"
    cur = conn.cursor()
    try:
        cur.executescript(sql_unicode61)
    except sqlite3.OperationalError:
        print "Could not use unicode61. You might have problems with accents. Please use a more recent QGIS version."
        cur.executescript(sql)

    conn.close()

def nDaysAgoIsoDate(nDays):
    return unicode( ( datetime.now() - timedelta(days=nDays) ).date().isoformat() )

class ProjectFinder(AbstractFinder):

    name = 'project'

    isValid = False
    version = '1.0'  # version of the SQLite file. Will be used if any changes to the format are made.
    stopLoop = False

    conn = None
    _searches = OrderedDict()

    recordingSearchProgress = pyqtSignal(int)
    fileChanged = pyqtSignal()

    @property
    def searches(self): return self._searches

    def __init__(self, parent):
        super(ProjectFinder, self).__init__(parent)
        self.reload()

    def reload(self):
        filepath = self.settings.value("qftsfilepath")
        self.setFile(filepath)

    def start(self, toFind, bbox=None):
        super(ProjectFinder, self).start(toFind, bbox)
        self.find(toFind)
        self._finish()

    def setFile(self, filepath):
        self.close()
        self.isValid = False

        try:
            f = open(filepath)
        except IOError:
            return

        self.conn = sqlite3.connect(filepath)
        if self.getInfo("scope") != "quickfinder":
            self.close()
            return

        self.isValid = True
        self._searches = self.readSearches()
        self.fileChanged.emit()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def getInfo(self, key):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT value FROM quickfinder_info WHERE key=?", [key])
            return cur.fetchone()[0]
        except sqlite3.OperationalError:
            return None

    def setInfo(self, key, value):
        if not self.isValid:
            return
        cur = self.conn.cursor()
        cur.execute("UPDATE quickfinder_info SET value = ? WHERE key = ?", [value, key])
        self.conn.commit()

    def readSearches(self):
        searches = OrderedDict()
        if not self.isValid:
            return searches
        sql = "SELECT search_id, search_name, layer_id, layer_name, expression, priority, srid, date_evaluated FROM quickfinder_toc ORDER BY date_evaluated ASC;"
        cur = self.conn.cursor()
        for s in cur.execute(sql):
            searches[s[0]] = ProjectSearch( s[0], s[1], s[2], s[3], s[4].replace("\\'","'"), s[5], s[6], s[7] )
        return searches

    def find(self, toFind):
        if self.settings.value("qftsfilepath") == '':
            return
        if not self.isValid:
            self.message.emit("Cannot search in project. QuickFinder file is probably currently in use.",QgsMessageBar.WARNING)
            return
        # add star after each word except numbers
        toFind = toFind.split(' ')
        for i,word in enumerate(toFind):
            try:
                int(word)
            except ValueError:
                toFind[i] = '%s*' % word
        toFind = ' '.join(toFind)
        # FTS request
        sql = "SELECT search_id,content,x,y,wkb_geom FROM quickfinder_data WHERE content MATCH ?"
        cur = self.conn.cursor()

        catLimit = self.settings.value("categoryLimit")
        totalLimit = self.settings.value("totalLimit")
        catFound = {}
        for row in cur.execute(sql, [toFind]):
            search_id, content, x, y, wkb_geom = row
            if catFound.has_key(search_id):
                if catFound[search_id] >= catLimit:
                    continue
                catFound[search_id] += 1
            else:
                catFound[search_id] = 1

            if not self._searches.has_key(search_id):
                continue

            geometry = QgsGeometry()
            geometry.fromWkb(binascii.a2b_hex(wkb_geom))

            crs = QgsCoordinateReferenceSystem()
            crs.createFromString(self._searches[search_id].srid)
            self.resultFound.emit(self,
                                  self._searches[search_id].searchName,
                                  content,
                                  geometry,
                                  crs.postgisSrid())

            if sum(catFound.values()) >= totalLimit:
                break

    def deleteSearch(self, searchId, commit=True):
        if not self.isValid:
            return False
        cur = self.conn.cursor()
        cur.execute("DELETE FROM quickfinder_data WHERE search_id = '{0}';".format(searchId))
        cur.execute("DELETE FROM quickfinder_toc WHERE search_id = '{0}';".format(searchId))
        self.conn.commit()
        self.optimize()
        return True

    def recordSearch(self, projectSearch, optimize=True):
        if not self.isValid:
            return False, "The index file is invalid. Use another one or create new one."

        layerid = projectSearch.layerid
        searchName = projectSearch.searchName
        priority = projectSearch.priority
        searchId = projectSearch.searchId
        expression = projectSearch.expression

        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not layer:
            projectSearch.status = "layer_deleted"
            return False, "Layer does not exist"

        today = unicode(date.today().isoformat())
        expression_esc = expression.replace("'", "\\'")  # escape simple quotes for SQL insert

        cur = self.conn.cursor()

        # always remove existing search with same id
        self.deleteSearch(searchId, False)

        sql = "INSERT INTO quickfinder_data (search_id, content, x, y, wkb_geom) VALUES ('{0}',?,?,?,?)".format(searchId)
        cur.executemany(sql, self.expressionIterator(layer, expression))

        if self.stopLoop:
            self.conn.rollback()
            return False, "Cancel by user"
        else:
            cur.execute( """INSERT INTO quickfinder_toc (search_id, search_name, layer_id, layer_name  , expression   , priority , date_evaluated, srid)
                            VALUES                      (?        , ?          , ?       , ?           , ?            , ?        , ?             , ?    ) """,
                                                        (searchId , searchName , layerid , layer.name(), expression_esc, priority, today         , layer.crs().authid()))
            self.conn.commit()

        if optimize:
            self.optimize()

        projectSearch.dateEvaluated = today
        return True, ""

    def optimize(self):
        print "optimize"
        cur = self.conn.cursor()
        cur.executescript("""INSERT INTO quickfinder_data(quickfinder_data) VALUES('rebuild');
                          INSERT INTO quickfinder_data(quickfinder_data) VALUES('optimize');
                          VACUUM;""")
        self.conn.commit()

    def expressionIterator(self, layer, expression):
        featReq = QgsFeatureRequest()
        qgsExpression = QgsExpression(expression)
        self.stopLoop = False
        i = 0
        for f in layer.getFeatures(featReq):
            QCoreApplication.processEvents()
            if self.stopLoop:
                break
            self.recordingSearchProgress.emit(i)
            i += 1
            evaluated = unicode(qgsExpression.evaluate(f))
            if qgsExpression.hasEvalError():
                continue
            if f.geometry() is None or f.geometry().centroid() is None:
                continue
            centroid = f.geometry().centroid().asPoint()
            wkb = binascii.b2a_hex(f.geometry().asWkb())
            yield ( evaluated, centroid.x(), centroid.y(), wkb )

    def stopRecord(self):
        self.stopLoop = True

