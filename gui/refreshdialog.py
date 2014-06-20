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


from PyQt4.QtGui import QDialog

from quickfinder.ui.ui_refresh import Ui_Refresh


class RefreshDialog(QDialog, Ui_Refresh):
    def __init__(self, localSearchModel):
        QDialog.__init__(self)
        self.setupUi(self)

        self.progressBar.hide()
        self.refreshButton.clicked.connect(self.refresh)

    def refresh(self):


        self.progressBar.show()

