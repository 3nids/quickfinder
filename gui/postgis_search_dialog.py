#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2017 Pirmin Kalberer, Sourcepole AG
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

from PyQt4.QtGui import QDialog
from ..ui.ui_postgissearch import Ui_PostgisSearch


class PostgisSearchDialog(QDialog, Ui_PostgisSearch):
    def __init__(self, postgis_finder, postgis_search_model, postgisSearch=None):
        QDialog.__init__(self)
        self.setupUi(self)

        self.postgis_finder = postgis_finder
        self.postgis_search_model = postgis_search_model
        self.postgisSearch = postgisSearch

        self.cancelButton.hide()
        self.okButton.clicked.connect(self.process)

        if postgisSearch is not None:
            self.searchName.setText(postgisSearch.searchName)
            self.queryEdit.setText(postgisSearch.expression)
            self.priorityBox.setValue(postgisSearch.priority)
            self.srid.setText(postgisSearch.srid)

    def process(self):
        search_name = self.searchName.text()
        expression = self.queryEdit.toPlainText()
        srid = self.srid.text()
        priority = self.priorityBox.value()

        if self.postgisSearch is None:
            self.postgisSearch = self.postgis_search_model.addSearch(search_name, expression, priority, srid)
        else:
            self.postgisSearch.edit(search_name, expression, priority, srid)

        ok, message = self.postgis_finder.recordSearch(self.postgisSearch)
        if not ok:
            QErrorMessage().showMessage(message)
            return

        self.close()
