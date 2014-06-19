'''
Created on 24 mars 2014

@author: arnaud
'''

from PyQt4.QtCore import QObject, pyqtSignal

from qgis.core import QgsGeometry
from qgis.gui import QgsMessageBar

from quickfinder.core.mysettings import MySettings


class AbstractFinder(QObject):

    name = ''  # to be defined in subclasses

    crs = None
    continueSearch = False
    transform = None  # to be defined by subclasses

    progress = pyqtSignal(QObject, int, int)  # total current
    resultFound = pyqtSignal(QObject, str, str, QgsGeometry)
    limitReached = pyqtSignal(QObject, str)
    finished = pyqtSignal(QObject)
    message = pyqtSignal(QObject, str, QgsMessageBar.MessageLevel)

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.settings = MySettings()

    def start(self, toFind, crs=None, bbox=None):
        self.crs = crs
        self.continueSearch = True

    def stop(self):
        self.continueSearch = False

    def activated(self):
        return MySettings().value(self.name)

    def _resultFound(self, layername, value, geometry):
        geometry = self._transform(geometry)
        if not geometry:
            self._finish()
            return False
        self.resultFound.emit(self, layername, value, geometry)
        return True

    def _transform(self, geometry):
        if self.transform:
            try:
                geometry.transform(self.transform)
            except:
                self.message.emit(self,
                                  'CRS transformation error!',
                                  QgsMessageBar.CRITICAL)
                self._finish()
                return
        return geometry

    def _finish(self):
        self.continueSearch = False
        self.finished.emit(self)

    def isRunning(self):
        return self.continueSearch
