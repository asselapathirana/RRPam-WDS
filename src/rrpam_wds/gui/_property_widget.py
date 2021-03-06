# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'property_widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class Ui_projectDataWidget(object):

    def setupUi(self, projectDataWidget):
        projectDataWidget.setObjectName("projectDataWidget")
        projectDataWidget.resize(527, 429)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(projectDataWidget.sizePolicy().hasHeightForWidth())
        projectDataWidget.setSizePolicy(sizePolicy)
        projectDataWidget.setMinimumSize(QtCore.QSize(320, 240))
        projectDataWidget.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.gridLayout = QtWidgets.QGridLayout(projectDataWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.asset_groups_and_assignments = QtWidgets.QTabWidget(projectDataWidget)
        self.asset_groups_and_assignments.setObjectName("asset_groups_and_assignments")
        self.asset_groups = QtWidgets.QWidget()
        self.asset_groups.setObjectName("asset_groups")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.asset_groups)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox = QtWidgets.QGroupBox(self.asset_groups)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.pg_verticalLayout = QtWidgets.QVBoxLayout()
        self.pg_verticalLayout.setObjectName("pg_verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.no_groups = QtWidgets.QSpinBox(self.groupBox)
        self.no_groups.setMinimum(1)
        self.no_groups.setObjectName("no_groups")
        self.horizontalLayout_2.addWidget(self.no_groups)
        spacerItem = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pg_verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layout5 = QtWidgets.QVBoxLayout()
        self.layout5.setObjectName("layout5")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_5 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_5.setGeometry(QtCore.QRect(0, 0, 451, 305))
        self.scrollAreaWidgetContents_5.setObjectName("scrollAreaWidgetContents_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_5)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.assetgroup_container_parent_layout = QtWidgets.QVBoxLayout()
        self.assetgroup_container_parent_layout.setObjectName("assetgroup_container_parent_layout")
        self.verticalLayout_5.addLayout(self.assetgroup_container_parent_layout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_5)
        self.layout5.addWidget(self.scrollArea)
        self.horizontalLayout.addLayout(self.layout5)
        self.pg_verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_7.addLayout(self.pg_verticalLayout, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_4, 0, 0, 1, 1)
        self.asset_groups_and_assignments.addTab(self.asset_groups, "")
        self.assign_assets = QtWidgets.QWidget()
        self.assign_assets.setObjectName("assign_assets")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.assign_assets)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.assign_assets)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.copytoselection = QtWidgets.QPushButton(self.groupBox_2)
        self.copytoselection.setMaximumSize(QtCore.QSize(250, 16777215))
        self.copytoselection.setObjectName("copytoselection")
        self.horizontalLayout_4.addWidget(self.copytoselection)
        self.grouptocopy = QtWidgets.QComboBox(self.groupBox_2)
        self.grouptocopy.setMaximumSize(QtCore.QSize(100, 16777215))
        self.grouptocopy.setObjectName("grouptocopy")
        self.horizontalLayout_4.addWidget(self.grouptocopy)
        self.select_diameter_button = QtWidgets.QPushButton(self.groupBox_2)
        self.select_diameter_button.setObjectName("select_diameter_button")
        self.horizontalLayout_4.addWidget(self.select_diameter_button)
        self.select_diameter_combobox = QtWidgets.QComboBox(self.groupBox_2)
        self.select_diameter_combobox.setObjectName("select_diameter_combobox")
        self.horizontalLayout_4.addWidget(self.select_diameter_combobox)
        spacerItem1 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.gridLayout_6.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.layoutx = QtWidgets.QGroupBox(self.groupBox_2)
        self.layoutx.setObjectName("layoutx")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutx)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.layoutx)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 435, 269))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.assign_asset_item_parent_layout = QtWidgets.QVBoxLayout()
        self.assign_asset_item_parent_layout.setObjectName("assign_asset_item_parent_layout")
        spacerItem2 = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.assign_asset_item_parent_layout.addItem(spacerItem2)
        self.verticalLayout_6.addLayout(self.assign_asset_item_parent_layout)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea_2)
        self.gridLayout_6.addWidget(self.layoutx, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_2, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.asset_groups_and_assignments.addTab(self.assign_assets, "")
        self.verticalLayout.addWidget(self.asset_groups_and_assignments)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(projectDataWidget)
        self.asset_groups_and_assignments.setCurrentIndex(1)
        self.asset_groups_and_assignments.currentChanged[
            'int'].connect(self.grouptocopy.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(projectDataWidget)

    def retranslateUi(self, projectDataWidget):
        _translate = QtCore.QCoreApplication.translate
        projectDataWidget.setWindowTitle(_translate("projectDataWidget", "Asset Data"))
        self.asset_groups.setToolTip(
            _translate("projectDataWidget",
                       "<html><head/><body><p>Provide parameters for asset groups here. </p></body></html>"))
        self.label.setText(_translate("projectDataWidget", "No. Groups"))
        self.asset_groups_and_assignments.setTabText(
            self.asset_groups_and_assignments.indexOf(self.asset_groups),
            _translate("projectDataWidget",
                       "Property Groups"))
        self.assign_assets.setToolTip(
            _translate("projectDataWidget",
                       "<html><head/><body><p>Assign each asset to an asset group here. </p></body></html>"))
        self.copytoselection.setText(_translate("projectDataWidget", "Assign to selection :"))
        self.select_diameter_button.setText(_translate("projectDataWidget", "Select diameter"))
        self.layoutx.setTitle(_translate("projectDataWidget", "Assigned Groups"))
        self.asset_groups_and_assignments.setTabText(
            self.asset_groups_and_assignments.indexOf(self.assign_assets),
            _translate("projectDataWidget",
                       "Assign Assets"))
