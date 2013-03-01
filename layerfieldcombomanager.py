"""
QGIS - Layer / Field Combos Manager

Denis Rouzaud
denis.rouzaud@gmail.com

This class is useful if you want to simply manage a layer combo with one
(or several) field combos. The field combos are filled with the names of
columns of the currently selected layer in the layer combo.

In your plugin, create first a LayerCombo:
self.LayerComboManager = LayerCombo(self.iface, self.layerComboWidget)
or
self.LayerComboManager = LayerCombo(self.iface, self.layerComboWidget, "MyLayerId", True, QGis.Point)

Then, associates some FieldCombo:
self.firstFieldComboManager = FieldCombo(self.firstFieldComboWidget, self.LayerComboManager )
or
self.firstFieldComboManager = FieldCombo(self.firstFieldComboWidget, self.LayerComboManager, lambda: self.settings.value("MyFieldName", "variablex"), QMetaType.QString )

You have to save the FieldCombo in self.something, so the variable is not
getting out of scope in python.

The classes offers some convenience methods:
LayerCombo: getLayer()
FieldCombo: getFieldName(), getFieldAlias(), getFieldIndex()
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

########################################################################
# creates a layer combo:
#
#    widget:      the qcombobox widget
#
#    initLayer:   the initally selected layer ID or a lambda function 
#                 returning the ID (it could look for a value in settings)
#
#    hasGeometry: True/False, restrain the possible selection of layers
#                 to layers having or not geometry 
#
#    geomType:    restrain the possible selection of layers to a certain
#                 type of geometry geomType must be a GeometryType 
#                 http://qgis.org/api/classQGis.html#a09947eb19394302eeeed44d3e81dd74b
#
class LayerCombo():
	def __init__(self, iface, widget, initLayer="", hasGeometry=None, geomType=None):
		self.layerType = None
		self.widget = widget
		self.initLayer = initLayer
		self.hasGeometry = hasGeometry
		self.geomType = geomType
		self.canvas = iface.mapCanvas()
		QObject.connect(self.canvas, SIGNAL("layersChanged ()") , self.__canvasLayersChanged )
		self.__canvasLayersChanged()
        
	def __canvasLayersChanged(self):
		self.widget.clear()
		self.widget.addItem("")
		if hasattr(self.initLayer,'__call__'):
			initLayer = self.initLayer()
		else:
			initLayer = self.initLayer
		for layer in self.canvas.layers():
			# only select vector layer
			if layer.type() != QgsMapLayer.VectorLayer:	continue
			# if wanted, filter on hasGeometry
			if self.hasGeometry is not None and layer.hasGeometryType() != self.hasGeometry: continue
			# if wanted, filter on the geoetry type
			if self.geomType is not None and layer.geometryType() != self.geomType:	continue
			self.widget.addItem( layer.name() , layer.id() )
			if layer.id() == initLayer:
				self.widget.setCurrentIndex( self.widget.count()-1 )
            
	def getLayer(self):
		i = self.widget.currentIndex()
		if i == 0: return None
		layerId = self.widget.itemData( i ).toString()
		return QgsMapLayerRegistry.instance().mapLayer( layerId )
		


########################################################################
# creates a field combo:
#
#    widget:    the qcombobox widget
#
#    layerCombo: the parent combobox defining the used layer
#
#    initField: the initially selected field name or a lambda function
#               returning the name (it could look for a value in settings)
#
#    fieldType: restrain the possible selection to a certain type of field
#
class FieldCombo():
	def __init__(self, widget, layerCombo, initField="", fieldType=None):
		self.widget = widget
		self.layerCombo = layerCombo
		self.initField = initField
		self.fieldType = fieldType
		QObject.connect(layerCombo.widget, SIGNAL("currentIndexChanged(int)"), self.__layerChanged)
		self.layer = None
		self.__layerChanged()

	def __layerChanged(self):
		if type(self.layer) == QgsVectorLayer:
			QObject.disconnect(self.layer, SIGNAL("attributeAdded(int)"),   self.__layerChanged)
			QObject.disconnect(self.layer, SIGNAL("attributeDeleted(int)"), self.__layerChanged)
		if hasattr(self.initField,'__call__'):
			initField = self.initField()
		else:
			initField = self.initField
		self.widget.clear()
		self.widget.addItem("")
		self.layer = self.layerCombo.getLayer()
		if self.layer is None: return
		QObject.connect(self.layer, SIGNAL("attributeAdded(int)"),   self.__layerChanged)
		QObject.connect(self.layer, SIGNAL("attributeDeleted(int)"), self.__layerChanged)
		i = 0
		for idx,field in enumerate(self.layer.pendingFields()):
			i += 1
			fieldAlias = self.layer.attributeDisplayName( idx )
			fieldName  = field.name()
			self.widget.addItem( fieldAlias , fieldName )
			if not self.__isFieldValid(idx):
				print "-->disable"
				j = self.widget.model().index(i,0)
				self.widget.model().setData(j, QVariant(0), Qt.UserRole-1)
				continue
			if fieldName == initField:
				self.widget.setCurrentIndex( i )
				
	def __isFieldValid(self, idx):
		if self.fieldType==None: return True
		return self.layer.dataProvider().fields()[idx].type() == self.fieldType
				
	def isValid(self):
		idx = self.getFieldIndex()
		if idx == -1: return False
		return self.__isFieldValid(idx)
                
	def getFieldAlias(self):
		i = self.widget.currentIndex()
		if i==0: return ""
		return self.widget.currentText()
		
	def getFieldName(self):
		i = self.widget.currentIndex()
		if i==0: return ""
		return self.widget.itemData( i ).toString()
		
	def getFieldIndex(self):
		i = self.widget.currentIndex()
		if i==0: return None
		return self.layer.fieldNameIndex( self.getFieldName() )
