'''
Created on 24 mars 2014

@author: arnaud
'''

import unicodedata

from PyQt4.QtCore import QObject, pyqtSignal

from qgis.core import QgsGeometry
from qgis.gui import QgsMessageBar


def remove_accents(data):
    # http://www.unicode.org/reports/tr44/#GC_Values_Table
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if unicodedata.category(x)[0] in ('L', 'N', 'P', 'Zs')).lower()


class BaseFinder(QObject):
    resultFound = pyqtSignal(str, str, str, QgsGeometry)
    finished = pyqtSignal()
    message = pyqtSignal(str, QgsMessageBar.MessageLevel)
    progress = pyqtSignal(int)

    def __init__(self):
        QObject.__init__(self)

    def stop(self):
        self.continueSearch = False

    def start(self, toFind, bbox=None):
        self.continueSearch = True
        print "search started"

    def isRunning(self):
        return not self.continueSearch
