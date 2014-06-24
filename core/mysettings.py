#-----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2014 Denis Rouzaud, Arnaud Morvan
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

from PyQt4.QtGui import QColor
from quickfinder.qgissettingmanager import SettingManager

pluginName = "quickfinder_plugin"


class MySettings(SettingManager):
    def __init__(self):
        SettingManager.__init__(self, pluginName)

        # general settings
        self.addSetting("historyLength", "integer", "global", 3)
        self.addSetting("categoryLimit", "integer", "global", 10)
        self.addSetting("totalLimit", "integer", "global", 80)

        # project settings
        self.addSetting("project", "bool", "project", True)
        self.addSetting("layerId", "string", "project", '')
        self.addSetting("fieldName", "string", "project", '')


        self.addSetting("qftsfilepath", "string", "project", '')

        # OpenStreetMap settings
        self.addSetting("osm", "bool", "project", True)
        self.addSetting("osmUrl", "string", "global",
                        'http://nominatim.openstreetmap.org/search')

        # GeoMapFish settings
        self.addSetting("geomapfish", "bool", "project", True)
        self.addSetting("geomapfishUrl", "string", "global",
                        'http://mapfish-geoportal.demo-camptocamp.com/demo/wsgi/fulltextsearch')
        self.addSetting("geomapfishCrs", "string", "global", 'EPSG:21781')

