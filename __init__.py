"""
Quick Finder
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
"""


def classFactory(iface):
    from quickfinder import quickFinder
    return quickFinder(iface)
