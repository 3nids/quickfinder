

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

class FtsConnection():

    isValid = False
    version = '1.0'

    conn = None

    def __init__(self, filepath=None):
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
        if not self.isValid:
            return
        searches = list()
        sql = "SELECT search_id, search_name, layer_id, layer_name, expression, priority, srid, date_evaluated FROM quickfinder_toc;"
        cur = self.conn.cursor()
        for s in cur.execute(sql):
            searches.append( LocalSearch( s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]) )
        return searches

    def evaluateExpression(self, layer, expression):
        featReq = QgsFeatureRequest()
        qgsExpression = QgsExpression(expression)
        for f in layer.getFeatures(featReq):
            evaluated = unicode(qgsExpression.evaluate(f))
            if qgsExpression.hasEvalError():
                continue
            centroid = f.geometry().centroid().asPoint()
            yield ( evaluated, centroid.x(), centroid.y() )

    def evaluateSearch(self, searchId, searchName, layerid, expression, priority):
        if not self.isValid:
            return False, "The index file is invalid. Use another one or create new one."

        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not layer:
            return False, "Layer does not exist"

        today = unicode(date.today().isoformat())
        expression_esc = expression.replace("'", "\\'")  # escape simple quotes for SQL insert

        cur = self.conn.cursor()
        sql = "INSERT INTO quickfinder_fts (search_id, evaluated, x, y) VALUES ('{0}',?,?,?)".format(searchId)
        cur.executemany(sql, self.evaluateExpression(layer, expression))
        self.conn.commit()

        sql = """INSERT INTO quickfinder_toc (search_id, search_name, layer_id, layer_name  , expression   , priority, date_evaluated, srid)
                       VALUES                ('{0}'    , '{1}'      , '{2}'   , '{3}'       , '{4}'        , {5}     , '{6}'         , '{7}' ) """.format(
                                             searchId  , searchName , layerid , layer.name(), expression_esc, priority, today         , layer.crs().authid() )

        print sql
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

        return True, today


