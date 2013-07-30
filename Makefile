#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/



# Makefile for a PyQGIS plugin 

# global
PLUGINNAME = quickfinder
PY_FILES = __init__.py $(PLUGINNAME).py
EXTRAS = metadata.txt resources.qrc
TOOL_DIR = gui core ui qgiscombomanager qgissettingmanager
ICONS_DIR = icons

UI_SOURCES=$(wildcard ui/*.ui)
UI_FILES=$(join $(dir $(UI_SOURCES)), $(notdir $(UI_SOURCES:%.ui=%.py)))
RC_SOURCES=$(wildcard *.qrc)
RC_FILES=$(patsubst %.qrc,%.py,$(RC_SOURCES))

GEN_FILES = ${UI_FILES} ${RC_FILES}

all: $(GEN_FILES)
ui: $(UI_FILES)
resources: $(RC_FILES)

$(UI_FILES): ui/%.py: ui/%.ui
	pyuic4 -o $@ $<

$(RC_FILES): %.py: %.qrc
	pyrcc4 -o $@ $<

clean:
	rm -f $(GEN_FILES) *.pyc

compile: $(UI_FILES) $(RESOURCE_FILES)

deploy:
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -rvf * $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/
