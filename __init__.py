"""
Quick Finder
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
"""

def name():
    return "Quick Finder"
def description():
    return "Dockable dialog to find a feature by its ID in a layer."
def version():
    return "Version 1.1"
def icon():
    return "icons/quickfinder.png"
def qgisMinimumVersion():
    return "1.8"
def classFactory(iface):
    from quickfinder import quickFinder
    return quickFinder(iface)
