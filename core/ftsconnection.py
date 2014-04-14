

from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest, QgsExpression

from datetime import date
from uuid import uuid1
import sqlite3






"""
version of the sqlite file.
"""

def createFTSfile(filepath):
    conn = sqlite3.connect(filepath)

    sql = "CREATE TABLE quickfinder_info (key text,value text);"
    sql += "INSERT INTO quickfinder_info (key,value) VALUES ('scope','quickfinder');"
    sql += "INSERT INTO quickfinder_info (key,value) VALUES ('db_version','1.0');"
    sql += "CREATE TABLE quickfinder_toc (search_id text, search_name text, layer_id text, layer_name text, expression text, priority integer, date_evaluated text, srid text);"
    sql += "CREATE VIRTUAL TABLE quickfinder_fts USING fts4 (search_id, evaluated, x real, y real);"
    cur = conn.cursor()
    cur.executescript(sql)
    conn.close()

class FtsConnection():

    isValid = False
    version = '1.0'

    def __init__(self, filepath=None):
        if filepath is None:
            return

        self.conn = sqlite3.connect(filepath)


        if self.getInfo("scope") != "quickfinder":
            self.close()
            return

        self.isValid = True

    def close(self):
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

    def evaluateExpression(self, layer, expression):
        featReq = QgsFeatureRequest()
        qgsExpression = QgsExpression(expression)
        for f in layer.getFeatures(featReq):
            evaluated = unicode(qgsExpression.evaluate(f))
            if qgsExpression.hasEvalError():
                continue
            centroid = f.geometry().centroid().asPoint()
            yield ( evaluated, centroid.x(), centroid.y() )

    def evaluateSearch(self,searchName, layerid, expression, priority):
        if not self.isValid:
            return False, "The index file is invalid. Use another one or create new one."

        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not layer:
            return False, "Layer does not exist"

        today = unicode(date.today().isoformat())
        search_id = unicode(uuid1())

        cur = self.conn.cursor()
        sql = "INSERT INTO quickfinder_fts (search_id, evaluated, x, y) VALUES ('{0}',?,?,?)".format(search_id)
        cur.executemany(sql, self.evaluateExpression(layer, expression))
        self.conn.commit()

        print (search_id, searchName, layerid, layer.name(), expression, priority, today         , layer.crs().authid())

        sql = """INSERT INTO quickfinder_toc (search_id, search_name, layer_id, layer_name  , expression, priority, date_evaluated, srid)
                       VALUES                ('{0}'    , '{1}'      , '{2}'   , '{3}'       , '{4}'     , {5}     , '{6}'         , '{7}' ) """.format(
                                             search_id, searchName , layerid , layer.name(), expression, priority, today         , layer.crs().authid() )
        print sql

        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()




        return True, ""


