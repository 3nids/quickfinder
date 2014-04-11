

from PyQt4.QtGui import QStandardItemModel, QStandardItem

from qgis.core import QgsProject, QgsMapLayerRegistry

from quickfinder.core.mysettings import MySettings


class ProjectLayersModel(QStandardItemModel):
    def __init__(self):
        QStandardItemModel.__init__(self)

        entries = MySettings().value("projectlayers")

        for i in range(0,len(entries),3):
            name = QStandardItem(entries[i])
            layerId = entries[i+1]
            layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
            if not layer:
                continue

            expression = QStandardItem(entries[i+2])



            self.insertRow(i/3, [name, layer, expression])





