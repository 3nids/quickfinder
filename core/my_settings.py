# -----------------------------------------------------------
#
# QGIS Quick Finder Plugin
# Copyright (C) 2014 Denis Rouzaud, Arnaud Morvan
#
# -----------------------------------------------------------
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
# ---------------------------------------------------------------------

from ..qgissettingmanager import SettingManager, Scope, Bool, String, Integer

pluginName = "quickfinder_plugin"


class MySettings(SettingManager):
    def __init__(self):
        SettingManager.__init__(self, pluginName)

        # general settings
        self.add_setting(Integer("historyLength", Scope.Global, 3))
        self.add_setting(Integer("categoryLimit", Scope.Global, 10))
        self.add_setting(Integer("totalLimit", Scope.Global, 80))

        # project settings
        self.add_setting(Bool("project", Scope.Project, False))
        self.add_setting(String("layerId", Scope.Project, ''))
        self.add_setting(String("fieldName", Scope.Project, ''))
        self.add_setting(String("qftsfilepath", Scope.Project, ''))
        self.add_setting(Bool("refreshAuto", Scope.Project, True))
        self.add_setting(Integer("refreshDelay", Scope.Project, 15))
        self.add_setting(String("refreshLastAsked", Scope.Project, ''))

        # OpenStreetMap settings
        self.add_setting(Bool("osm", Scope.Global, True))
        self.add_setting(String("osmUrl", Scope.Global,'http://nominatim.openstreetmap.org/search'))

        # GeoMapFish settings
        self.add_setting(Bool("geomapfish", Scope.Global, True))
        self.add_setting(String("geomapfishUrl", Scope.Global, 'http://mapfish-geoportal.demo-camptocamp.com/1.5/search'))
        self.add_setting(String("geomapfishCrs", Scope.Global, 'EPSG:3857'))
        self.add_setting(String("geomapfishUser", Scope.Global, ''))
        self.add_setting(String("geomapfishPass", Scope.Global, ''))
