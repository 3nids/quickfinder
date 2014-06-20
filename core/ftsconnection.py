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

from PyQt4.QtCore import pyqtSignal, QObject, QCoreApplication

from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest, QgsExpression

from datetime import date
import sqlite3

from quickfinder.core.localsearch import LocalSearch




"""
version of the sqlite file.
"""

def createFTSfile(filepath):
    conn = sqlite3.connect(filepath)

    sql = "CREATE TABLE quickfinder_info (key text,value text);"
    sql += "INSERT INTO quickfinder_info (key,value) VALUES ('scope','quickfinder');"
    sql += "INSERT INTO quickfinder_info (key,value) VALUES ('db_version','1.0');"
    sql += "CREATE TABLE quickfinder_toc (search_id text, search_name text, layer_id text, layer_name text, expression text, priority integer, srid text, date_evaluated text);"
    sql += "CREATE VIRTUAL TABLE quickfinder_fts USING fts4 (search_id, evaluated, x real, y real);"
    cur = conn.cursor()
    cur.executescript(sql)
    conn.close()

class FtsConnection(QObject):

    isValid = False
    version = '1.0'
    stopLoop = False

    conn = None

    recordingSearchProgress = pyqtSignal(int)

    def __init__(self, filepath=None):
        QObject.__init__(self)
        if filepath is None:
            return
        self.setFile(filepath)

    def setFile(self, filepath):
        self.close()

        self.conn = sqlite3.connect(filepath)

        if self.getInfo("scope") != "quickfinder":
            self.isValid = False
            self.close()
            return

        self.isValid = True

    def close(self):
        if self.conn is not None:
            self.conn.close()

    def getInfo(self, key):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT value FROM quickfinder_info WHERE key='%s'" % key)
            return cur.fetchone()[0]
        except sqlite3.OperationalError:
            return None


    def exeSql(self, sql):
        c = self.conn.cursor()
        c.execute(sql)
        self.conn.commit()

    def searches(self):
        searches = list()
        if not self.isValid:
            return searches
        sql = "SELECT search_id, search_name, layer_id, layer_name, expression, priority, srid, date_evaluated FROM quickfinder_toc;"
        cur = self.conn.cursor()
        for s in cur.execute(sql):
            searches.append( LocalSearch( s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]) )
        return searches

    def recordSearch(self, localSearch):
        if not self.isValid:
            return False, "The index file is invalid. Use another one or create new one."

        layerid = localSearch.layerid
        searchName = localSearch.searchName
        priority = localSearch.priority
        searchId = localSearch.searchId
        expression = localSearch.expression


        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not layer:
            localSearch.status = "layer_deleted"
            return False, "Layer does not exist"

        today = unicode(date.today().isoformat())
        expression_esc = expression.replace("'", "\\'")  # escape simple quotes for SQL insert

        cur = self.conn.cursor()
        sql = "INSERT INTO quickfinder_fts (search_id, evaluated, x, y) VALUES ('{0}',?,?,?)".format(searchId)
        cur.executemany(sql, self.expressionIterator(layer, expression))

        if self.stopLoop:
            self.conn.rollback()
            return False, "Cancel by user"
        else:
            cur.execute( """INSERT INTO quickfinder_toc (search_id, search_name, layer_id, layer_name  , expression   , priority , date_evaluated, srid)
                            VALUES                      (?        , ?          , ?       , ?           , ?            , ?        , ?             , ?    ) """,
                                                        (searchId , searchName , layerid , layer.name(), expression_esc, priority, today         , layer.crs().authid()))
            self.conn.commit()

        localSearch.dateEvaluated = today
        localSearch.status = "evaluated"
        return True, ""

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
            centroid = f.geometry().centroid().asPoint()
            yield ( evaluated, centroid.x(), centroid.y() )

    def stopRecord(self):
        self.stopLoop = True

