"""
Quick Finder
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from layer_field_combo import LayerCombo,FieldCombo
from ui_quickfinder import Ui_quickFinder

class FinderDock(QDockWidget , Ui_quickFinder ):
	def __init__(self,iface):
		self.iface = iface
		# UI setup
		QDockWidget.__init__(self)
		self.setupUi(self)
		self.iface.addDockWidget(Qt.LeftDockWidgetArea,self)
		self.layerComboManager = LayerCombo(iface, self.layerCombo)
		FieldCombo(self.fieldCombo, self.layerComboManager)
		QObject.connect(self.layerCombo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
		self.setVisible(False)

	def enable(self,trueOrFalse):
		self.idLine.setEnabled(trueOrFalse)
		self.idButton.setEnabled(trueOrFalse)
		self.columnButton.setEnabled(trueOrFalse)
		if self.columnButton.isChecked():
			self.fieldCombo.setEnabled(trueOrFalse)
		else:
			self.fieldCombo.setEnabled(False)
		self.panBox.setEnabled(trueOrFalse)
		self.scaleBox.setEnabled(trueOrFalse)
		self.selectBox.setEnabled(trueOrFalse)
		self.formBox.setEnabled(trueOrFalse)
		self.goButton.setEnabled(trueOrFalse)
	
	def layerChanged(self,i):
		# reset
		self.enable(False)
		self.idLine.clear()
		layer = self.layerComboManager.getLayer()
		if layer is None: return
		self.enable(True)
		if layer.hasGeometryType() is False:
			self.panBox.setEnabled(False)
			self.scaleBox.setEnabled(False)
		
	@pyqtSignature("on_goButton_pressed()")
	def on_goButton_pressed(self):
		i = self.layerCombo.currentIndex()
		if i < 1: return
		# get layer from list
		layer = self.layerComboManager.getLayer()
		id,ok = self.idLine.text().toInt()
		if ok is False:
			QMessageBox.warning( self.iface.mainWindow() , "Quick Finder","ID must be strictly composed of digits." )
			return
		f = QgsFeature()
		try:
			if layer.getFeatures( QgsFeatureRequest().setFilterFid( id ) ).nextFeature( f ) is False: return	
		except: # qgis <1.9
			if layer.dataProvider().featureAtId(id,f,True,layer.dataProvider().attributeIndexes()) is False: return
		if self.selectBox.isChecked():
			layer.setSelectedFeatures([id])
		if self.panBox.isEnabled() and self.panBox.isChecked():
			bobo = f.geometry().boundingBox()
			if self.scaleBox.isEnabled() and self.scaleBox.isChecked() and bobo.width() != 0 and bobo.height() != 0:
				bobo.scale( 3 )
			else:
				panTo  = bobo.center()
				bobo = self.iface.mapCanvas().extent()
				xshift  = panTo.x() - bobo.center().x()
				yshift  = panTo.y() - bobo.center().y()
				x0 = bobo.xMinimum() + xshift
				y0 = bobo.yMinimum() + yshift
				x1 = bobo.xMaximum() + xshift
				y1 = bobo.yMaximum() + yshift
				bobo.set(x0,y0,x1,y1)		
			self.iface.mapCanvas().setExtent(bobo)
			self.iface.mapCanvas().refresh()				
		if self.formBox.isChecked():
			self.iface.openFeatureForm(layer, f )
