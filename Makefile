#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/



# Makefile for a PyQGIS plugin 

PLUGINNAME =$(shell basename $(CURDIR))

QGISDIR=.qgis2

PY_FILES = __init__.py $(PLUGINNAME).py
EXTRAS = metadata.txt resources.qrc
TOOL_DIR = gui core ui qgiscombomanager qgissettingmanager
ICONS_DIR = icons

UI_SOURCES=$(wildcard ui/*.ui)
UI_FILES=$(join $(dir $(UI_SOURCES)), $(notdir $(UI_SOURCES:%.ui=%.py)))
RC_SOURCES=$(wildcard *.qrc)
RC_FILES=$(join $(dir $(RC_SOURCES)), $(notdir $(RC_SOURCES:%.qrc=%_rc.py)))

GEN_FILES = ${UI_FILES} ${RC_FILES}

all: $(GEN_FILES)
ui: $(UI_FILES)
resources: $(RC_FILES)

$(UI_FILES): ui/%.py: ui/%.ui
	pyuic4 -o $@ $<

$(RC_FILES): %_rc.py: %.qrc
	pyrcc4 -o $@ $<

clean:
	rm -f $(GEN_FILES)
	find $(CURDIR) -iname "*.pyc" -delete

compile: $(UI_FILES) $(RC_FILES)

deploy: compile
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -rvf * $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/
	rm -f $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/$(PLUGINNAME).zip

# The dclean target removes compiled python files from plugin directory
dclean:
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	rm -f $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/$(PLUGINNAME).zip

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

zip: clean deploy dclean
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)
