# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_neb_explorer.ui'
#
# Created: Sat Jan 26 03:59:19 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionRun = QtGui.QAction(MainWindow)
        self.actionRun.setObjectName(_fromUtf8("actionRun"))
        self.actionE = QtGui.QAction(MainWindow)
        self.actionE.setCheckable(True)
        self.actionE.setChecked(True)
        self.actionE.setObjectName(_fromUtf8("actionE"))
        self.actionS = QtGui.QAction(MainWindow)
        self.actionS.setCheckable(True)
        self.actionS.setChecked(True)
        self.actionS.setObjectName(_fromUtf8("actionS"))
        self.actionK = QtGui.QAction(MainWindow)
        self.actionK.setCheckable(True)
        self.actionK.setChecked(True)
        self.actionK.setObjectName(_fromUtf8("actionK"))
        self.actionRms = QtGui.QAction(MainWindow)
        self.actionRms.setCheckable(True)
        self.actionRms.setChecked(True)
        self.actionRms.setObjectName(_fromUtf8("actionRms"))
        self.actionNimages = QtGui.QAction(MainWindow)
        self.actionNimages.setCheckable(True)
        self.actionNimages.setChecked(True)
        self.actionNimages.setObjectName(_fromUtf8("actionNimages"))
        self.action3D = QtGui.QAction(MainWindow)
        self.action3D.setCheckable(True)
        self.action3D.setObjectName(_fromUtf8("action3D"))
        self.toolBar.addAction(self.actionE)
        self.toolBar.addAction(self.actionS)
        self.toolBar.addAction(self.actionK)
        self.toolBar.addAction(self.actionNimages)
        self.toolBar.addAction(self.actionRms)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "NEB explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRun.setText(QtGui.QApplication.translate("MainWindow", "Run", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRun.setToolTip(QtGui.QApplication.translate("MainWindow", "run the neb", None, QtGui.QApplication.UnicodeUTF8))
        self.actionE.setText(QtGui.QApplication.translate("MainWindow", "E", None, QtGui.QApplication.UnicodeUTF8))
        self.actionE.setToolTip(QtGui.QApplication.translate("MainWindow", "show energies", None, QtGui.QApplication.UnicodeUTF8))
        self.actionS.setText(QtGui.QApplication.translate("MainWindow", "s", None, QtGui.QApplication.UnicodeUTF8))
        self.actionS.setToolTip(QtGui.QApplication.translate("MainWindow", "path length", None, QtGui.QApplication.UnicodeUTF8))
        self.actionK.setText(QtGui.QApplication.translate("MainWindow", "k", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRms.setText(QtGui.QApplication.translate("MainWindow", "rms", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNimages.setText(QtGui.QApplication.translate("MainWindow", "nimages", None, QtGui.QApplication.UnicodeUTF8))
        self.action3D.setText(QtGui.QApplication.translate("MainWindow", "3D", None, QtGui.QApplication.UnicodeUTF8))

