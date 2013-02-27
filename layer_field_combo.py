"""
QGIS - Layer Field Combo class

Denis Rouzaud
denis.rouzaud@gmail.com

This class is useful if you want to simply manage a layer combo with one (or several) field combos.
The field combos are filled with the column name of the currently selected layer in the layer combo.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# creates a layer combo:
# 	combo: the qcombobox widget
#	geomType: restrain the possible selection of layers to a certain type of geometry [not working yet]
#	initLayer: a lambda function returning the ID of the initially selected layer (it could look for a value in settings)
class LayerCombo(QObject):
	layerChanged = pyqtSignal()
	
	def __init__(self,iface,widget,geomType=None,initLayer=lambda:""):
		self.widget = widget
		self.initLayer = initLayer
		self.geomType = geomType
		self.canvas = iface.mapCanvas()
		QObject.__init__(self)
		QObject.connect(self.canvas, SIGNAL("layersChanged ()") , self.canvasLayersChanged )
		QObject.connect(widget, SIGNAL("currentIndexChanged(int)"), self.currentLayerChanged)
		self.canvasLayersChanged()
		
	def canvasLayersChanged(self):
		self.widget.clear()
		self.widget.addItem("")
		for layer in self.canvas.layers():
			if layer.type() != QgsMapLayer.VectorLayer:
				continue
			# TODO check geom  or layer.hasGeometryType() is False
			self.widget.addItem( layer.name() , layer.id() )
			if layer.id() == self.initLayer(): self.combo.setCurrentIndex()
			
	def getLayer(self):
		i = self.widget.currentIndex()
		if i == 0: return None
		layerId = self.widget.itemData( i ).toString()
		return QgsMapLayerRegistry.instance().mapLayer( layerId )
		
	def currentLayerChanged(self,i):
		self.layerChanged.emit()
		print "layercombo: layer changed"
		error_msg = ''
		#if i > 0:
		#	layer = self.layerList[i-1]
		#	# TODO CHECK GEOMETRY
		#	print "TODO CHECK GEOMETRY",layer.dataProvider().geometryType() , layer.geometryType()
		#if error_msg != '':
		#	self.dimensionLayerCombo.setCurrentIndex(0)
		#	QMessageBox.warning( self , "Bad Layer", error_msg )
		



# creates a field combo:
# 	combo: the qcombobox widget
#	fieldType: restrain the possible selection to a certain type of field
#	initField: a lambda function returning the name of the initially selected field (it could look for a value in settings)
class FieldCombo(QObject):
	def __init__(self,widget,layerCombo,fieldType=None,initField=lambda:""):
		self.widget = widget
		self.layerCombo = layerCombo
		self.initField = initField
		self.fieldType = fieldType
		QObject.__init__(self)
		
		QObject.connect(widget, SIGNAL("currentIndexChanged(int)"), self.fieldChanged)

		QObject.connect(self.layerCombo.widget, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
		self.layerCombo.layerChanged.connect( self.layerChanged )
		
		self.layerChanged()

	def layerChanged(self):
		print "fieldcombo: layer changed"
		self.widget.clear()
		self.widget.addItem("")
		layer = self.layerCombo.getLayer()
		if layer is None: return
		for i,fieldItem in enumerate( layer.dataProvider().fieldNameMap() ):
			self.widget.addItem( fieldItem )
			if fieldItem == self.initField():
				self.widget.setCurrentIndex(i+1)		
				
	def fieldChanged(self,i):
		print "fieldcombo: field changed"
		if i < 1 or checkType is None: return
		layer = self.layerCombo.getLayer()
		if layer is None: return
		fieldName = self.widget.currentText()
		i = self.getLayer().dataProvider().fieldNameIndex( fieldName )
		# http://qgis.org/api/classQgsField.html#a00409d57dc65d6155c6d08085ea6c324
		# http://developer.qt.nokia.com/doc/qt-4.8/qmetatype.html#Type-enum
		if self.getLayer().dataProvider().fields()[i].type() != self.fieldType:
			QMessageBox.warning( self , "Bad field" ,  QApplication.translate("Layer Field Combo", "The field must be a %s" % self.fieldType, None, QApplication.UnicodeUTF8) )
			field.combo.setCurrentIndex(0)
	
