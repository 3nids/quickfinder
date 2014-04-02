
import unicodedata, time

from PyQt4.QtCore import QCoreApplication

from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest, \
                        QgsFeature, QgsGeometry, QgsCoordinateTransform
from qgis.gui import QgsMessageBar

from basefinder import BaseFinder
from quickfinder.core.mysettings import MySettings


def remove_accents(data):
    # http://www.unicode.org/reports/tr44/#GC_Values_Table
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if unicodedata.category(x)[0] in ('L', 'N', 'P', 'Zs')).lower()


class ProjectFinder(BaseFinder):

    name = 'Project'

    def __init__(self, parent):
        super(ProjectFinder, self).__init__(parent)

    def activated(self):
        return MySettings().value('project')

    def start(self, toFind, crs=None, bbox=None):
        super(ProjectFinder, self).start(toFind, crs, bbox)

        self.toFind = toFind

        # give search parameters to thread
        layerId = MySettings().value("layerId")
        self.layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        if self.layer is None:
            self._finish()
            return

        self.transform = None
        if self.crs.authid() != self.layer.crs().authid():
            self.transform = QgsCoordinateTransform(self.layer.crs(), self.crs)

        self.field = MySettings().value("fieldName")
        if self.field is None:
            self._finish()
            return
        self.isExpression = False

        self.operator = 6

        print self.name, "start loop"
        chrono = time.time()

        featReq = QgsFeatureRequest()
        if not self.isExpression:
            fieldIndex = self.layer.fieldNameIndex(self.field)
            featReq.setSubsetOfAttributes([fieldIndex])
        # featReq.setFlags(QgsFeatureRequest.NoGeometry)

        layerlimit = MySettings().value("layerlimit")
        total = self.layer.pendingFeatureCount()
        current = 0
        found = 0

        f = QgsFeature()
        for f in self.layer.getFeatures(featReq):
            current += 1
            self.progress.emit(self, total, current)
            QCoreApplication.processEvents()

            if not self.continueSearch:
                break

            if self.evaluate(f):
                feat = f

                '''
                featReq = QgsFeatureRequest()
                fieldIndex = self.layer.fieldNameIndex(self.field)
                featReq.setFilterFid(f.id())
                for feat in self.layer.getFeatures(featReq):
                '''

                if not self.isExpression:
                    value = feat[self.field]
                else:
                    value = self.field.evaluate(feat)

                if not self._resultFound(self.layer.name(),
                                        value,
                                        QgsGeometry(feat.geometry())):
                    return

                found += 1
                if found >= layerlimit:
                    self.limitReached.emit(self, self.layer.name())
                    self._finish()
                    return

        # '%H:%M:%S'
        duration = time.strftime('%X', time.localtime(time.time() - chrono))
        print self.name, "end loop, duration :", duration

        self._finish()

    def evaluate(self, f):
        if not self.isExpression:
            value = f[self.field]
        else:
            value = self.field.evaluate(f)
            if self.operator == 6:
                value = str(value)
            elif self.operator in (1, 2, 3, 4, 5):
                try:
                    value = float(value)
                except ValueError:
                    self.message.emit(self, "Expression result must be numeric for chosen operator", QgsMessageBar.WARNING)
                    return False

        if self.operator == 0:
            return value == self.toFind
        elif self.operator == 1:
            return float(value) == float(self.toFind)
        elif self.operator == 2:
            return float(value) <= float(self.toFind)
        elif self.operator == 3:
            return float(value) >= float(self.toFind)
        elif self.operator == 4:
            return float(value) < float(self.toFind)
        elif self.operator == 5:
            return float(value) > float(self.toFind)
        elif self.operator == 6:
            try:
                # print self.__class__.__name__, 'evaluate', value, self.toFind
                remove_accents(unicode(value)).index(remove_accents(self.toFind))
                return True
            except ValueError:
                return False
