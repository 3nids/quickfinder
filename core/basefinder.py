'''
Created on 24 mars 2014

@author: arnaud
'''

import unicodedata

from PyQt4.QtCore import QObject, pyqtSignal

from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.gui import QgsMessageBar

from quickfinder.core.mysettings import MySettings


def remove_accents(data):
    # http://www.unicode.org/reports/tr44/#GC_Values_Table
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if unicodedata.category(x)[0] in ('L', 'N', 'P', 'Zs')).lower()


class BaseFinder(QObject):

    name = ''  # to be defined in subclasses

    continueSearch = False
    limit = 10

    progress = pyqtSignal(QObject, int, int)  # total current
    resultFound = pyqtSignal(QObject, str, str, QgsGeometry)
    limitReached = pyqtSignal(QObject, str)
    finished = pyqtSignal(QObject)
    message = pyqtSignal(QObject, str, QgsMessageBar.MessageLevel)

    def __init__(self, parent):
        QObject.__init__(self, parent)

    def start(self, toFind, bbox=None):
        print self.__class__.__name__, "start"
        self.continueSearch = True
        self.limit = MySettings().value("limit")

    def stop(self):
        print self.__class__.__name__, "stop"
        self.continueSearch = False

    def _finish(self):
        print self.__class__.__name__, "_finish"
        self.continueSearch = False
        self.finished.emit(self)

    def isRunning(self):
        return self.continueSearch
