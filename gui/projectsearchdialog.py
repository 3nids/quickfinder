

from PyQt4.QtGui import QDialog

from qgis.gui import QgsMapLayerProxyModel

from quickfinder.ui.ui_projectsearch import Ui_ProjectSearch



class ProjectSearchDialog(QDialog, Ui_ProjectSearch):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        self.layerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.layerCombo.layerChanged.connect(self.fieldExpressionWidget.setLayer)
        self.fieldExpressionWidget.setLayer(self.layerCombo.currentLayer())

        self.searchName.setText('test')
