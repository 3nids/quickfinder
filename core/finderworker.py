
import unicodedata

from PyQt4.QtCore import QObject, pyqtSignal

from qgis.core import QgsFeature, QgsFeatureRequest
from qgis.gui import QgsMessageBar


def remove_accents(data):
    # http://www.unicode.org/reports/tr44/#GC_Values_Table
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if unicodedata.category(x)[0] in ('L', 'N', 'P', 'Zs')).lower()


class FinderWorker(QObject):
    resultFound = pyqtSignal(QgsFeature)
    finished = pyqtSignal()
    message = pyqtSignal(str, QgsMessageBar.MessageLevel)
    progress = pyqtSignal(int)

    def __init__(self):
        self.continueSearch = True

    def define(self, layer, field, isExpression, operator, toFind):
        self.layer = layer
        self.field = field
        self.isExpression = isExpression
        self.operator = operator
        self.toFind = toFind

    def stop(self):
        self.continueSearch = False


    def process(self):
        self.continueSearch = True

        f = QgsFeature()

        # feature at id
        pk = self.layer.pendingPkAttributesList()
        fid = None
        idOk = True
        try:
            fid = long(self.toFind)
        except ValueError:
            idOk = False
        if pk.count() == 1 and idOk and self.layer.getFieldNameIndex(self.field) == pk[0]:
            if self.layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).nextFeature(f):
                self.resultFound.emit(f)
            else:
                self.message.emit("No features found at id", QgsMessageBar.INFO)
            self.finished.emit()
            return

        # Standard search
        fieldIndex = self.fieldComboManager.getFieldIndex()

        if self.operator in (1, 2, 3, 4, 5):
            try:
                float(self.toFind)
            except ValueError:
                self.message.emit("Value must be numeric for chosen operator", QgsMessageBar.WARNING)
                self.finished.emit()
                return

        featReq = QgsFeatureRequest().setSubsetOfAttributes([fieldIndex])
        k = 0
        for f in self.layer.getFeatures(featReq):
            k += 1
            if not self.continueSearch:
                break
            if self.evaluate(f):
                self.resultFound.emit(f)
            self.progress.emit(k)

        self.finished.emit()

    def evaluate(self, f):

        if not self.isExpression:
            value = f[self.field]

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
