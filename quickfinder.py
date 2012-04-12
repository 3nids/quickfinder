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

import resources

from ui_quickfinder import Ui_quickFinder

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class quickFinder():
	def __init__(self, iface):
		self.iface = iface
		self.dock  = finderDock(iface)
		QObject.connect(self.iface.mapCanvas() , SIGNAL("layersChanged ()") , self.dock.canvasLayersChanged ) 
		
	def initGui(self):
		# dock
		self.dockAction = QAction(QIcon(":/plugins/quickfinder/icons/quickfinder.png"), "Quick Finder", self.iface.mainWindow())
		self.dockAction.setCheckable(True)
		QObject.connect(self.dockAction, SIGNAL("triggered(bool)"), self.dock.setVisible)
		self.iface.addPluginToMenu("&Quick Finder", self.dockAction)	
		self.iface.addToolBarIcon(self.dockAction)
		QObject.connect(self.dock, SIGNAL("visibilityChanged(bool)"), self.dockAction.setChecked )
		# help
		self.helpAction = QAction(QIcon(":/plugins/quickfinder/icons/help.png"), "Help", self.iface.mainWindow())
		QObject.connect(self.helpAction, SIGNAL("triggered()"), lambda: QDesktopServices.openUrl(QUrl("https://github.com/3nids/quickfinder/wiki")))
		self.iface.addPluginToMenu("&Quick Finder", self.helpAction)
				
	def unload(self):
		# Remove the plugin menu item and icon
		self.iface.removePluginMenu("&Quick Finder",self.dockAction)
		self.iface.removePluginMenu("&Quick Finder",self.helpAction)
		self.iface.removeToolBarIcon(self.dockAction)



class finderDock(QDockWidget , Ui_quickFinder ):
	def __init__(self,iface):
		self.iface = iface
		# UI setup
		QDockWidget.__init__(self)
		self.setupUi(self)
		self.iface.addDockWidget(Qt.LeftDockWidgetArea,self)
		self.setVisible(False)
		self.layerList = []
		self.curLayerID = []

	def enable(self,trueOrFalse):
		self.idLine.setEnabled(trueOrFalse)
		self.idLabel.setEnabled(trueOrFalse)
		self.panBox.setEnabled(trueOrFalse)
		self.scaleBox.setEnabled(trueOrFalse)
		self.selectBox.setEnabled(trueOrFalse)
		self.formBox.setEnabled(trueOrFalse)
		self.goButton.setEnabled(trueOrFalse)
	
	def canvasLayersChanged(self):
		self.enable(False)
		self.layerList = self.iface.mapCanvas().layers()
		self.layerCombo.clear()
		self.layerCombo.addItem("")
		for i,layer in enumerate(self.layerList):
			self.layerCombo.addItem(layer.name())
			if layer.id() == self.curLayerID: self.layerCombo.setCurrentIndex(i+1)

	@pyqtSignature("on_layerCombo_currentIndexChanged(int)")
	def on_layerCombo_currentIndexChanged(self,i):
		# reset
		self.enable(False)
		self.idLine.clear()
		if i < 1: return
		# get layer from list
		layer = self.layerList[i-1]
		self.curLayerID = layer.id()
		# check layer
		if layer.type() != QgsMapLayer.VectorLayer: return
		self.enable(True)
		if layer.hasGeometryType() is False:
			self.panBox.setEnabled(False)
			self.scaleBox.setEnabled(False)
		
	@pyqtSignature("on_goButton_clicked()")
	def on_goButton_clicked(self):
		i = self.layerCombo.currentIndex()
		if i < 1: return
		# get layer from list
		layer = self.layerList[i-1]
		id,ok = self.idLine.text().toInt()
		if ok is False:
			QMessageBox.warning( self.iface.mainWindow() , "Quick Finder","ID must be strictly composed of digits." )
			return
		f = QgsFeature()
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
