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


from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QDialog

from quickfinder.ui.ui_refresh import Ui_Refresh


class RefreshDialog(QDialog, Ui_Refresh):

    stop = False
    searchProgress = 0
    currentLayerLength = 0

    def __init__(self, projectFinder, projectSearchModel, selectedRows):
        QDialog.__init__(self)
        self.setupUi(self)

        self.projectFinder = projectFinder
        self.projectSearchModel = projectSearchModel
        self.selectedRows = selectedRows

        self.progressBar.hide()
        self.cancelButton.hide()

        self.cancelButton.clicked.connect(self.cancel)
        self.refreshButton.clicked.connect(self.refresh)

        self.projectFinder.recordingSearchProgress.connect(self.setProgress)

    def refresh(self):
        searches = self.projectSearchModel.searches

        self.stop = False
        self.cancelButton.show()
        self.refreshButton.hide()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(searches)*100)  # progressBar only accepts int, so scaling
        self.progressBar.show()

        unrec = self.unrecordedRadio.isChecked()
        selec = self.selectedRadio.isChecked()
        delet = self.deletedLayersCheckBox.isChecked()

        self.searchProgress = -1
        for search in searches:
            QCoreApplication.processEvents()

            self.searchProgress += 1
            self.currentLayerLength = 0
            self.setProgress()

            # user stop
            if self.stop:
                break

            # delete search if layer has been deleted
            layer = search.layer()
            if layer is None and delet:
                if self.projectFinder.deleteSearch(search.searchId):
                    del self.projectSearchModel.searches[search.searchId]
                continue

            # if specified only process non evaluated searches
            if unrec and search.dateEvaluated is not None:
                continue

            # if specified only do selected rows
            if selec and search.searchId not in self.selectedRows:
                continue

            self.currentLayerLength = layer.featureCount()
            ok, message = self.projectFinder.recordSearch(search, True)

        self.progressBar.hide()
        self.cancelButton.hide()
        self.refreshButton.show()

    def closeEvent(self, e):
        self.cancel()
        e.accept()

    def cancel(self):
        self.projectFinder.stopRecord()
        self.stop = True

    def setProgress(self, value=0):
        p = self.searchProgress
        if self.currentLayerLength!=0:
            p += float(value) / self.currentLayerLength
        p *= 100
        self.progressBar.setValue(p)


