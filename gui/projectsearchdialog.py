

from PyQt4.QtGui import QDialog

from qgis.gui import QgsMapLayerProxyModel

from quickfinder.ui.ui_projectsearch import Ui_ProjectSearch



class ProjectSearchDialog(QDialog, Ui_ProjectSearch):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        self.layerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.layerCombo.layerChanged.connect(self.fieldCombo.setLayer)
        self.fieldCombo.setLayer(self.layerCombo.currentLayer())
        self.expressionButton.setFieldCombo(self.fieldCombo)

        self.searchName.setText('test')


    def editConfig(self, layer, field):
        self.layerCombo.setLayer(layer)
        self.fieldCombo.setField(field)

