
import unicodedata

from PyQt4.QtCore import QCoreApplication

from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest, QgsFeature, QgsGeometry
from qgis.gui import QgsMessageBar

from basefinder import BaseFinder
from quickfinder.core.mysettings import MySettings


def remove_accents(data):
    # http://www.unicode.org/reports/tr44/#GC_Values_Table
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if unicodedata.category(x)[0] in ('L', 'N', 'P', 'Zs')).lower()


class ProjectFinder(BaseFinder):

    def __init__(self):
        BaseFinder.__init__(self)

    def define(self, layer, field, isExpression, operator):
        self.layer = layer
        self.field = field
        self.isExpression = isExpression
        self.operator = operator

    def start(self, toFind, bbox=None):
        BaseFinder.start(self, toFind, bbox)

        self.toFind = toFind

        # give search parameters to thread
        layerId = MySettings().value("layerId")
        self.layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        if self.layer is None:
            return

        self.field = MySettings().value("fieldName")
        self.isExpression = False
        if self.field is None:
            return

        self.operator = 6

        f = QgsFeature()

        print "start loop"
        featReq = QgsFeatureRequest()
        if self.isExpression:
            fieldIndex = self.layer.getFieldNameIndex(self.field)
            featReq.setSubsetOfAttributes([fieldIndex])
        k = 0
        for f in self.layer.getFeatures(featReq):
            QCoreApplication.processEvents()
            k += 1
            if not self.continueSearch:
                break
            if self.evaluate(f):
                if not self.isExpression:
                    value = f[self.field]
                else:
                    value = self.field.evaluate(f)
                self.resultFound.emit('project', self.layer.name(), value, f.geometry())
            self.progress.emit(k)
        self.finished.emit()

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
                    self.message.emit("Expression result must be numeric for chosen operator", QgsMessageBar.WARNING)
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
                remove_accents(unicode(value)).index(remove_accents(self.toFind))
                return True
            except ValueError:
                return False
