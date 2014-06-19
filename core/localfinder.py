
import unicodedata

from PyQt4.QtCore import QCoreApplication

from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest, \
                        QgsFeature, QgsGeometry, QgsCoordinateTransform
from qgis.gui import QgsMessageBar

from abstractfinder import AbstractFinder
from ftsconnection import FtsConnection


def remove_accents(data):
    # http://www.unicode.org/reports/tr44/#GC_Values_Table
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if unicodedata.category(x)[0] in ('L', 'N', 'P', 'Zs')).lower()


class LocalFinder(AbstractFinder):

    name = 'Project'
    ftsConn = FtsConnection()

    def __init__(self, parent):
        super(LocalFinder, self).__init__(parent)
        self.reload()

    def reload(self):
        filepath = self.settings.value("qftsfilepath")
        self.ftsConn = FtsConnection(filepath)

    def start(self, toFind, crs=None, bbox=None):
        super(LocalFinder, self).start(toFind, crs, bbox)

        self.toFind = toFind



        self._finish()

