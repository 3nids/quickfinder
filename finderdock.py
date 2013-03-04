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
		self.layerComboManager = LayerCombo(iface, self.layerCombo)
		self.fieldComboManager = FieldCombo(self.fieldCombo, self.layerComboManager)
		QObject.connect(self.layerCombo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
		QObject.connect(self.modeButtonGroup, SIGNAL("buttonClicked(int)"), self.layerChanged)
		QObject.connect(self.fieldCombo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
		self.layer = None
		self.operatorBox.hide()
		self.processWidgetGroup.hide()
		self.layerChanged(0)
		self.setVisible(False)

	def layerChanged(self,i):
		self.modeWidgetGroup.setEnabled(False)
		self.searchWidgetGroup.setEnabled(False)
		self.idLine.clear()
		self.layer = self.layerComboManager.getLayer()
		if self.layer is None:
			return
		self.modeWidgetGroup.setEnabled(True)
		if self.fieldButton.isChecked() and self.fieldCombo.currentIndex()==0:
			return
		self.searchWidgetGroup.setEnabled(True)
		self.on_selectBox_clicked()
			
	@pyqtSignature("on_selectBox_clicked()")
	def on_selectBox_clicked(self):
		if self.layer is None or not self.selectBox.isChecked():
			self.panBox.setEnabled(False)
			self.scaleBox.setEnabled(False)
		else:
			self.panBox.setEnabled( self.layer.hasGeometryType() )
			self.scaleBox.setEnabled( self.layer.hasGeometryType() )
		
	@pyqtSignature("on_cancelButton_pressed()")
	def on_cancelButton_pressed(self):
		self.continueSearch = False

	@pyqtSignature("on_goButton_pressed()")
	def on_goButton_pressed(self):
		i = self.layerCombo.currentIndex()
		if i < 1 or self.layer is None: return
		toFind = self.idLine.text()
		f = QgsFeature()
		if self.idButton.isChecked():
			id,ok = toFind.toInt()
			if ok is False:
				QMessageBox.warning( self.iface.mainWindow() , "Quick Finder","ID must be strictly composed of digits." )
				return
			try:
				if self.layer.getFeatures( QgsFeatureRequest().setFilterFid( id ) ).nextFeature( f ) is False: return
			except: # qgis <1.9
				if self.layer.dataProvider().featureAtId(id,f,True,self.layer.dataProvider().attributeIndexes()) is False: return
			self.processResults( [f.id()] )
		else:
			results = []
			fieldName  = self.fieldComboManager.getFieldName()
			fieldIndex = self.fieldComboManager.getFieldIndex()
			if fieldName=="": return
			operator = self.operatorBox.currentIndex()
			# show progress bar
			self.progressBar.setMinimum(0)
			self.progressBar.setMaximum(self.layer.featureCount())
			self.progressBar.setValue(0)
			self.processWidgetGroup.show()
			# disable rest of UI
			self.layerWidgetGroup.setEnabled(False)
			self.modeWidgetGroup.setEnabled(False)
			self.searchWidgetGroup.setEnabled(False)
			# create feature request
			try:
				featReq = QgsFeatureRequest()
				featReq.setSubsetOfAttributes( [fieldIndex] )
				iter = self.layer.getFeatures(featReq)
			except:
				iter = self.layer.dataProvider()
				iter.select( [fieldIndex] )
			# process
			k=0
			self.continueSearch = True
			while( iter.nextFeature( f ) and self.continueSearch):
				k+=1
				try:
					value = f.attribute( fieldName )
				except:
					value = f.attributeMap()[fieldIndex]
				if self.evaluate(value, toFind, operator):
					results.append( f.id() )
				self.progressBar.setValue(k)
				QCoreApplication.processEvents()
			# reset UI
			self.processWidgetGroup.hide()
			self.layerWidgetGroup.setEnabled(True)
			self.modeWidgetGroup.setEnabled(True)
			self.searchWidgetGroup.setEnabled(True)
			# process results
			if self.continueSearch:
				self.processResults( results )
				
	def evaluate(self, v1, v2, operator):
		if operator == 0:
			return v1.toString() == v2
		elif operator == 1:
			return v1.toDouble()[0] == v2.toDouble()[0]
		elif operator == 2:
			return v1.toDouble()[0] <= v2.toDouble()[0]
		elif operator == 3:
			return v1.toDouble()[0] >= v2.toDouble()[0]
		elif operator == 4:
			return v1.toDouble()[0] <  v2.toDouble()[0]
		elif operator == 5:
			return v1.toDouble()[0] >  v2.toDouble()[0]
		elif operator == 6:
			return v1.toString().contains(v2, Qt.CaseInsensitive)

	def processResults(self, results):
		if self.layer is None: return

		if self.selectBox.isChecked():
			self.layer.setSelectedFeatures(results)
			if len(results)==0: return
			
			if self.panBox.isEnabled() and self.panBox.isChecked():
				canvas = self.iface.mapCanvas()
				rect = canvas.mapRenderer().layerExtentToOutputExtent( self.layer, self.layer.boundingBoxOfSelected() )
				if self.scaleBox.isChecked():
					canvas.setExtent( rect.scale(1.5) )
				else:
					canvas.setExtent( QgsRectangle( rect.center(), rect.center() ) )
				canvas.refresh()				
		if self.formBox.isChecked():
			nResults = len(results)
			if nResults > 25: return
			if nResults > 3:
				reply = QMessageBox.question( self.iface.mainWindow() , "Quick Finder", "%s results were found. Are you sure to open the %s feature forms ?" % (nResults,nResults), QMessageBox.Yes, QMessageBox.No )			
				if reply == QMessageBox.No: return
			f = QgsFeature()
			try:
				for id in results:
					if self.layer.getFeatures( QgsFeatureRequest().setFilterFid( id ) ).nextFeature( f ):
						self.iface.openFeatureForm(self.layer, f )
			except:
				for id in results:
					if self.layer.featureAtId(id, f):
						self.iface.openFeatureForm(self.layer, f )
