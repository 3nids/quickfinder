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

from layerfieldcombomanager import LayerCombo,FieldCombo
from ui_quickfinder import Ui_quickFinder

class FinderDock(QDockWidget , Ui_quickFinder ):
	startSearch = pyqtSignal(QgsVectorLayer,int,str,int,int)
	
	def __init__(self,iface):
		self.iface = iface
		QDockWidget.__init__(self)
		self.setupUi(self)
		self.iface.addDockWidget(Qt.LeftDockWidgetArea,self)
		self.layerComboManager = LayerCombo(iface, self.layerCombo,"",True)
		self.fieldComboManager = FieldCombo(self.fieldCombo, self.layerComboManager)
		QObject.connect(self.layerCombo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
		QObject.connect(self.modeButtonGroup, SIGNAL("buttonClicked(int)"), self.layerChanged)
		QObject.connect(self.fieldCombo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
		self.signBox.hide()
		self.processWidgetGroup.hide()
		self.layerChanged(0)
		self.setVisible(False)

	def layerChanged(self,i):
		self.modeWidgetGroup.setEnabled(False)
		self.searchWidgetGroup.setEnabled(False)
		self.idLine.clear()
		layer = self.layerComboManager.getLayer()
		if layer is None:
			return
		self.modeWidgetGroup.setEnabled(True)
		if self.fieldButton.isChecked() and self.fieldCombo.currentIndex()==0:
			return
		self.searchWidgetGroup.setEnabled(True)
		if layer.hasGeometryType() is False:
			self.panBox.setEnabled(False)
			self.scaleBox.setEnabled(False)
		
	@pyqtSignature("on_cancelButton_pressed()")
	def on_cancelButton_pressed(self):
		self.continueSearch = False

	@pyqtSignature("on_goButton_pressed()")
	def on_goButton_pressed(self):
		i = self.layerCombo.currentIndex()
		if i < 1: return
		layer = self.layerComboManager.getLayer()
		toFind = self.idLine.text()
		results = []
		f = QgsFeature()
		if self.idButton.isChecked():
			id,ok = toFind.toInt()
			if ok is False:
				QMessageBox.warning( self.iface.mainWindow() , "Quick Finder","ID must be strictly composed of digits." )
				return
			try:
				if layer.getFeatures( QgsFeatureRequest().setFilterFid( id ) ).nextFeature( f ) is False: return
			except: # qgis <1.9
				if layer.dataProvider().featureAtId(id,f,True,layer.dataProvider().attributeIndexes()) is False: return
			results.append( f )
			self.processResults( results )
		else:
			self.progressBar.setMinimum(0)
			self.progressBar.setMaximum(layer.featureCount())
			self.progressBar.setValue(0)
			self.processWidgetGroup.show()
			fieldName  = self.fieldComboManager.getFieldName()
			fieldIndex = self.fieldComboManager.getFieldIndex()
			if fieldName=="": return
			featReq = QgsFeatureRequest()
			featReq.setSubsetOfAttributes( [fieldIndex] )
			iter = layer.getFeatures(featReq)
			k=0
			self.continueSearch = True
			while( iter.nextFeature( f ) and self.continueSearch):
				print k
				k+=1
				if f.attribute( fieldName ).toString() == toFind:				
					results.append( f )
				self.progressBar.setValue(k)
				QCoreApplication.processEvents()
			if self.continueSearch:
				self.processResults( results )
			
	def processResults(self, results):
		print "#results: ",len(results)		
		return
		
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
			
