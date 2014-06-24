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

    def __init__(self, localFinder, localSearchModel):
        QDialog.__init__(self)
        self.setupUi(self)

        self.localFinder = localFinder
        self.localSearchModel = localSearchModel

        self.progressBar.hide()
        self.cancelButton.hide()

        self.cancelButton.clicked.connect(self.cancel)
        self.refreshButton.clicked.connect(self.refresh)

        self.localFinder.recordingSearchProgress.connect(self.setProgress)

    def refresh(self):
        searches = self.localSearchModel.searches

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

            if self.stop:
                break

            if search.layer is None:
                # todo delete search entry
                continue

            self.currentLayerLength = search.layer.featureCount()

            if unrec and search.dateEvaluated is not None:
                continue

            #todo skip non selected

            ok, message = self.localFinder.recordSearch(search, True)

        self.progressBar.hide()
        self.cancelButton.hide()
        self.refreshButton.show()

    def cancel(self):
        self.localFinder.stopRecord()
        self.stop = True

    def setProgress(self, value=0):
        p = self.searchProgress
        if self.currentLayerLength!=0:
            p += float(value) / self.currentLayerLength
        p *= 100
        self.progressBar.setValue(p)


