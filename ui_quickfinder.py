# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_quickfinder.ui'
#
# Created: Thu Apr 12 16:33:51 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_quickFinder(object):
    def setupUi(self, quickFinder):
        quickFinder.setObjectName(_fromUtf8("quickFinder"))
        quickFinder.resize(275, 185)
        quickFinder.setWindowTitle(QtGui.QApplication.translate("quickFinder", "Quick Finder", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_2.setMargin(6)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.frame = QtGui.QFrame(self.dockWidgetContents)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.formLayout_2 = QtGui.QFormLayout(self.frame)
        self.formLayout_2.setMargin(6)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText(QtGui.QApplication.translate("quickFinder", "Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.layerCombo = QtGui.QComboBox(self.frame)
        self.layerCombo.setObjectName(_fromUtf8("layerCombo"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.layerCombo)
        self.idLabel = QtGui.QLabel(self.frame)
        self.idLabel.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.idLabel.sizePolicy().hasHeightForWidth())
        self.idLabel.setSizePolicy(sizePolicy)
        self.idLabel.setText(QtGui.QApplication.translate("quickFinder", "ID", None, QtGui.QApplication.UnicodeUTF8))
        self.idLabel.setObjectName(_fromUtf8("idLabel"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.idLabel)
        self.idLine = QtGui.QLineEdit(self.frame)
        self.idLine.setEnabled(False)
        self.idLine.setObjectName(_fromUtf8("idLine"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.idLine)
        self.widget = QtGui.QWidget(self.frame)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(3)
        self.gridLayout.setSpacing(3)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.widget_2 = QtGui.QWidget(self.widget)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.formLayout = QtGui.QFormLayout(self.widget_2)
        self.formLayout.setMargin(3)
        self.formLayout.setMargin(0)
        self.formLayout.setSpacing(3)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.scaleBox = QtGui.QCheckBox(self.widget_2)
        self.scaleBox.setEnabled(False)
        self.scaleBox.setText(QtGui.QApplication.translate("quickFinder", "scale", None, QtGui.QApplication.UnicodeUTF8))
        self.scaleBox.setObjectName(_fromUtf8("scaleBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.scaleBox)
        self.selectBox = QtGui.QCheckBox(self.widget_2)
        self.selectBox.setEnabled(False)
        self.selectBox.setText(QtGui.QApplication.translate("quickFinder", "select", None, QtGui.QApplication.UnicodeUTF8))
        self.selectBox.setChecked(True)
        self.selectBox.setObjectName(_fromUtf8("selectBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.selectBox)
        self.panBox = QtGui.QCheckBox(self.widget_2)
        self.panBox.setEnabled(False)
        self.panBox.setText(QtGui.QApplication.translate("quickFinder", "pan", None, QtGui.QApplication.UnicodeUTF8))
        self.panBox.setObjectName(_fromUtf8("panBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.panBox)
        self.formBox = QtGui.QCheckBox(self.widget_2)
        self.formBox.setEnabled(False)
        self.formBox.setText(QtGui.QApplication.translate("quickFinder", "open form", None, QtGui.QApplication.UnicodeUTF8))
        self.formBox.setObjectName(_fromUtf8("formBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.formBox)
        self.gridLayout.addWidget(self.widget_2, 0, 0, 1, 1)
        self.goButton = QtGui.QPushButton(self.widget)
        self.goButton.setEnabled(False)
        self.goButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.goButton.setText(QtGui.QApplication.translate("quickFinder", "Go", None, QtGui.QApplication.UnicodeUTF8))
        self.goButton.setObjectName(_fromUtf8("goButton"))
        self.gridLayout.addWidget(self.goButton, 0, 1, 1, 1)
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.SpanningRole, self.widget)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)
        quickFinder.setWidget(self.dockWidgetContents)

        self.retranslateUi(quickFinder)
        QtCore.QObject.connect(self.idLine, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.goButton.click)
        QtCore.QMetaObject.connectSlotsByName(quickFinder)
        quickFinder.setTabOrder(self.goButton, self.selectBox)
        quickFinder.setTabOrder(self.selectBox, self.formBox)
        quickFinder.setTabOrder(self.formBox, self.panBox)
        quickFinder.setTabOrder(self.panBox, self.idLine)
        quickFinder.setTabOrder(self.idLine, self.scaleBox)
        quickFinder.setTabOrder(self.scaleBox, self.layerCombo)

    def retranslateUi(self, quickFinder):
        pass

