"""
QGIS - Layer / Field Combos Manager

Denis Rouzaud
denis.rouzaud@gmail.com

This class is useful if you want to simply manage a layer combo with one
(or several) field combos. The field combos are filled with the names of
columns of the currently selected layer in the layer combo.
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
class LayerCombo(QObject):
	def __init__(self, iface, widget, initLayer="", hasGeometry=None, geomType=None):
		self.widget = widget
		self.initLayer = initLayer
		self.hasGeometry = hasGeometry
		self.geomType = geomType
		self.canvas = iface.mapCanvas()
		QObject.__init__(self)
		QObject.connect(self.canvas, SIGNAL("layersChanged ()") , self.canvasLayersChanged )
		self.canvasLayersChanged()
        
	def canvasLayersChanged(self):
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
			if self.hasGeometry is not None and layer.hasGeometry != self.hasGeometry: continue
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
class FieldCombo(QObject):
	def __init__(self, widget, layerCombo, initField="", fieldType=None):
		self.widget = widget
		self.layerCombo = layerCombo
		self.initField = initField
		self.fieldType = fieldType
		QObject.__init__(self)
		QObject.connect(widget, SIGNAL("currentIndexChanged(int)"), self.fieldChanged)
		QObject.connect(layerCombo.widget, SIGNAL("currentIndexChanged(int)"), self.layerChanged)
		self.layerChanged()

	def layerChanged(self):
		if hasattr(self.initField,'__call__'):
			initField = self.initField()
		else:
			initField = self.initField
		self.widget.clear()
		self.widget.addItem("")
		layer = self.layerCombo.getLayer()
		if layer is None: return
		for i,fieldItem in enumerate( layer.dataProvider().fieldNameMap() ):
			self.widget.addItem( fieldItem )
			if fieldItem == initField:
				self.widget.setCurrentIndex(i+1)        
                
	def fieldChanged(self,i):
		if i < 1 or self.fieldType is None: return
		layer = self.layerCombo.getLayer()
		if layer is None: return
		fieldName = self.widget.currentText()
		i = self.getLayer().dataProvider().fieldNameIndex( fieldName )
		# http://qgis.org/api/classQgsField.html#a00409d57dc65d6155c6d08085ea6c324
		# http://developer.qt.nokia.com/doc/qt-4.8/qmetatype.html#Type-enum
		if self.getLayer().dataProvider().fields()[i].type() != self.fieldType:
			QMessageBox.warning( self , "Field has an incorrect type" ,  QApplication.translate("Layer Field Combo", "The field must be a %s" % self.fieldType, None, QApplication.UnicodeUTF8) )
			field.combo.setCurrentIndex(0)

