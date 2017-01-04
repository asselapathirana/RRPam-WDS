from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA

import logging
import math
import sys

from guidata.configtools import get_icon
from guiqwt.builder import make
from guiqwt.plot import CurveDialog
from guiqwt.shapes import EllipseShape
from guiqwt.styles import style_generator
from guiqwt.styles import update_style_attr
from numpy import arange
from numpy import array
from numpy import interp
from numpy import max
from numpy import min
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QVBoxLayout

import rrpam_wds.config
import rrpam_wds.constants as c
import rrpam_wds.gui.subdialogs
import rrpam_wds.gui.utils as u
from rrpam_wds.constants import curve_colors
from rrpam_wds.constants import units
from rrpam_wds.gui import _property_widget
from rrpam_wds.gui.custom_toolbar_items import (ResetZoomTool, PlotWLCTool)
from rrpam_wds.logger import EmittingLogger
from rrpam_wds.logger import setup_logging
from rrpam_wds.project_manager import ProjectManager as PM

STYLE = style_generator()


class PropertyGroupGUI(QObject):

    logger = logging.getLogger()

    def __init__(self, frame):
        self.active = False
        self.frame = frame

        super(PropertyGroupGUI, self).__init__()

    def show(self):
        self.active = True
        self.frame.show()

    def hide(self):
        self.active = False
        self.frame.hide()


class AssetGUI(QObject):
    logger = logging.getLogger()

    def __init__(self, frame, datawindow):
        self.active = False
        self.frame = frame
        self.datawindow = datawindow
        super(AssetGUI, self).__init__()

    def my_group_changed(self, val):
        self.logger.info("*** my group changed %s" % val)
        self.datawindow.assets_group_changed_reciever(self.id_, val)

    def _selected_change_color(self, select):
        self.my_selected.setProperty("selected", False)

        if(select):
            self.my_selected.setProperty('selected', "true")
        else:
            self.my_selected.setProperty('selected', "false")

        self.my_selected.style().unpolish(self.my_selected)
        self.my_selected.style().polish(self.my_selected)

    def selected(self):
        if(hasattr(self, "my_selected")):
            # self.logger.info("returning my (%s) checkbox state" % self)
            return self.my_selected.isChecked()
        self.logger.info("No checkbox in me (%s), so returning False for selected state." % self)
        return False

    def select(self, select=True):
        if(hasattr(self, "my_selected")):
            # self.logger.info("making me (%s) selected=%s" % (self, select))
            self.my_selected.setChecked(select)
        else:
            self.logger.info("No checkbox in me (%s). So ignoring select request." % self)


class LogDialog(QDialog):

    def __init__(self, parent=None):
        super(LogDialog, self).__init__()
        self.parent = parent
        self.logwindow = QPlainTextEdit(parent=self.parent)
        self.logwindow.setReadOnly(True)
        self.logwindow.setStyleSheet("QPlainTextEdit {background-color:gray}")
        layout = QVBoxLayout(self)
        layout.addWidget(self.logwindow)
        self.setWindowIcon(get_icon("log_file.png"))
        self.setWindowTitle("Log record")

    @pyqtSlot(object)
    def reciever(self, object):
        # print("I Got: ", str(object))
        if (QApplication.instance()):
            # ^^ this is done as a safeguard of segfaults when called many tests together in pytest
            # Sometimes this method is called when there is no vailid Qapplication instance
            #  then appendPlainText segfaults.
            self.logwindow.appendPlainText(object)

    def get_text(self):
        return self.logwindow.toPlainText()

    def closeEvent(self, evnt):
        evnt.ignore()
        self.parent.hide_log_window()


class DataWindow(QDialog):
    groups_changed = pyqtSignal(list)
    myselectionchanged_signal = pyqtSignal(object)

    def __init__(self, mainwindow, parent=None):

        super(DataWindow, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Data Editor")
        self.setWindowIcon(get_icon("data.png"))
        self.initialize_assetgroups()
        self.initalize_assign_asset_groups()
        self.selected_holder = mainwindow.selected_holder
        self.mainwindow = mainwindow
        self.setup_ui()
        self.customize_ui()
        self.connect_signals()
        self._update_all()  # always call this at the end of _init_

    def getProb(self, id_, time_):
        grname = self.myplotitems[id_].my_group.currentIndex()
        age = self.get_age(id_)
        diameter, length = self.get_dims(id_)
        d, grs = self.get_information()
        gr = grs[grname]
        A = gr[0]
        N = gr[1]
        return length / c.LENGTH_CONVERSION_FACTOR[self.lunits] * N * math.exp(A * (age + time_))

    def draw_network(self, links):
        # get the units
        self.dunits = self.mainwindow.projectgui.projectproperties.dataset.dunits
        self.lunits = self.mainwindow.projectgui.projectproperties.dataset.lunits

        logger = logging.getLogger()
        if(not links):
            logger.info("Links sent was None. Ignoring request to draw!")
            return
        logger.info("Creating assignment items for %d links " % len(links))

        for link in links:
            self.add_assign_asset_item(link)
        spacerItem = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.ui.assign_asset_item_parent_layout.addItem(spacerItem)
        
        # now populate select_diameter_combobox with unique diameters
        dia=[str(y) for y in sorted(set(x.diameter_ for x in self.myplotitems.values()))]
        self.ui.select_diameter_combobox.clear()
        self.ui.select_diameter_combobox.addItems(dia)

    def _update_all(self):
        self._set_no_groups(1)

    def get_items(self):
        return self.myplotitems.values()

    def select_some_items(self, list_):
        logger = logging.getLogger()
        try:
            for target in self.myplotitems.values():
                target.select(False)
            for target in list_:
                target.select()
        except Exception as e:
            logger.exception("Error at select_some_items (%s) " % e)

    def myselectionchanged(self, state):
        logger = logging.getLogger()
        logger.info("Passing on a signal with my reference...")
        self.myselectionchanged_signal.emit(self)

    def initalize_assign_asset_groups(self):
        self.myplotitems = {}
        if(hasattr(self, 'ui')):
            layout = self.ui.assign_asset_item_parent_layout
            self._delete_all_children_in_layout(layout)

    def initialize_assetgroups(self):
        logger = logging.getLogger()
        logger.info("Initializing assetgrouplist=[] and activenumberofgroups=0 ")
        self.assetgrouplist = []
        self.activenumberofgroups = 0
        if(hasattr(self, 'ui')):
            layout = self.ui.assetgroup_container_parent_layout
            self._delete_all_children_in_layout(layout)

    def _delete_all_children_in_layout(self, layout):
        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if(w):
                w.hide()
                w.setParent(None)
                w.deleteLater()

    def setup_ui(self):
        self.ui = _property_widget.Ui_projectDataWidget()
        self.ui.setupUi(self)
        # self.ui.no_groups.valueChanged.disconnect()

    def connect_signals(self):
        self.ui.no_groups.valueChanged.connect(self._set_no_groups)
        self.groups_changed.connect(self._update_groupchoices)
        self.myselectionchanged_signal.connect(self.selected_holder)
        self.ui.select_diameter_button.pressed.connect(self._select_all_with_this_diameter)
        self.ui.copytoselection.pressed.connect(self._assign_group_to_selected_assets)

    def _deselect_all(self):
        logger = logging.getLogger()
        logger.info("Deselecting all.. ")
        [x.my_selected.setChecked(False) for x in self.myplotitems.values()]
        
    @pyqtSlot()
    def _assign_group_to_selected_assets(self):
        group=self.ui.grouptocopy.currentText()
        logger = logging.getLogger()
        logger.info("Copying group %s to selected." % group )  
        [x.my_group.setCurrentText(group) for x in self.get_selected_items()]
        
        
    @pyqtSlot()
    def _select_all_with_this_diameter(self):
        diameter=self.ui.select_diameter_combobox.currentText()
        logger = logging.getLogger()
        self._deselect_all()
        logger.info("Selecting diameter %s " % diameter )        
        [x.my_selected.setChecked(True) for x in self.myplotitems.values() if c.isclose(float(x.diameter_),float(diameter))]

    def _update_groupchoices(self, listofgroups):
        logger = logging.getLogger()
        logger.info("Updating grouptocopy choices and my_group choices.")
        self.ui.grouptocopy.clear()
        self.ui.grouptocopy.addItems(listofgroups)
        for myc in self.myplotitems.values():
            # listofgroups come with correct order exploit that and minimize work here.
            co = myc.my_group.count()
            if(co < len(listofgroups)):
                myc.my_group.addItems(listofgroups[co:])
            if (co > len(listofgroups)):
                for i in range(len(listofgroups), co):
                    myc.my_group.removeItem(i)
            # t = myc.my_group.currentIndex()
            # myc.my_group.clear()
            # myc.my_group.addItems(listofgroups)
            # if(co - 1 < t):
            #    t = co - 1
            # myc.my_group.setCurrentIndex(t)

    def customize_ui(self):
        self.spacerItem1 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)

    def get_plot(self):
        """This weird method is here so that this object confirms to the pattern
        of other sub-window types (which all have plots). In this case we just return a referene
        to this object. """
        return self

    def get_selected_items(self):
        """we are mimicking get_selected_items method of guiqwt.BasePlot widget"""
        return [x for x in self.myplotitems.values() if x.selected()]

    def get_dims(self, id):
        logger = logging.getLogger()
        try:
            return (self.myplotitems[id].diameter_, self.myplotitems[id].length_)
        except Exception:
            logger.exception("Error retrieving dimensions for id %s" % id)

    def get_age(self, id):
        logger = logging.getLogger()
        try:
            return self.myplotitems[id].my_age.value()
        except Exception:
            logger.exception("Error retrieving my_group for id %s" % id)

    def get_asset_group(self, id):
        logger = logging.getLogger()
        try:
            return self.myplotitems[id].my_group.currentIndex()
        except Exception:
            logger.exception("Error retrieving my_group for id %s" % id)

    def get_information(self, all=False):
        """This method returns active data of assetgrouplist (activenumberofgroups) - e.g. for calculations.
        if all=True, then it will return ALL items in assetgrouplist (e.g. for saving)"""
        if (not all):
            gr = [(float(x.A.text()), float(x.N0.text()))
                  for x in self.assetgrouplist[:self.activenumberofgroups]]
            return self.activenumberofgroups, gr
        else:
            return self.activenumberofgroups, [(float(x.A.text()), float(x.N0.text())) for x in self.assetgrouplist]

    def assign_values_to_asset_items(self, assets):
        logger = logging.getLogger()
        try:
            for item in assets:
                it = self.myplotitems[item.id]
                it.my_group.setCurrentIndex(item.asset_group)
                it.my_age.setValue(item.age)
        except Exception:
            logger.exception("Exception at assign_values_to_asset_items")

    def set_information(self, results_):
        logger = logging.getLogger()
        try:
            active = int(results_[0])  # just in case it is a string!
            results = results_[1]
            self.initialize_assetgroups()
            logger.info("Now adding asset groups ...")
            for ct, value in enumerate(results):
                logger.info("Now adding asset group: %d, %s" % (ct, value))
                self.add_assetgroup(ct, value)
            self.ui.activenumbrerofgroups = active
            self.ui.no_groups.setValue(active)
            self._set_no_groups(active)
            # this is needed, as ^^ we change the value manually, signal does not
            # fire.
        except Exception:
            logger.exception("Error in setting information:")

    def _set_no_groups(self, ngroups):
        # first remove that spacer
        self.ui.assetgroup_container_parent_layout.removeItem(self.spacerItem1)
        need = ngroups - self.activenumberofgroups
        self.activenumberofgroups = ngroups
        logger = logging.getLogger()
        if(need > 0):
            logger.info("Need %d number of asset groups more." % need)
            needtocreate = ngroups - len(self.assetgrouplist)
            st = len(self.assetgrouplist)
            if(needtocreate > 0):
                logger.info("Need to create %d new" % needtocreate)
                for i in range(needtocreate):
                    self.add_assetgroup(st + i)
        # now unhide
        logger.info("Unhiding from 0 to %d" % ngroups)
        for i in range(ngroups):
            self.assetgrouplist[i].show()
        logger.info("Hiding from %d to %d" % (ngroups, len(self.assetgrouplist)))
        for i in range(ngroups, len(self.assetgrouplist)):
            self.assetgrouplist[i].hide()

        # now add the spacer
        self.ui.assetgroup_container_parent_layout.addItem(self.spacerItem1)
        items = list(self.ui.assetgroup_container_parent_layout.itemAt(i)
                     for i in range(self.ui.assetgroup_container_parent_layout.count()))
        logger.info("List of widgets: %s " % items)
        logger.info("Sending signal: group choices updated.")
        self.groups_changed.emit([self._getgroupname(i) for i in range(self.activenumberofgroups)])

    def add_plot_item_to_record(self, id_, item):
        """All the plot items register here by calling this method. See also: remove_plot_item_from_record"""
        # TODO : CurveDialogWithClosable currently copies this function
        # need to implement multiple inheritance and make DRY
        self.myplotitems[id_] = item

    def remove_plot_item_from_record(self, id_):
        """When removing a plot item it should be notified to this function. See also: add_plot_item_to_record """
        # TODO : CurveDialogWithClosable currently copies this function
        # need to implement multiple inheritance and make DRY
        del self.myplotitems[id_]

    def assets_group_changed_reciever(self, id_, index):
        self.mainwindow.assets_group_changed_reciever(id_)

    def add_assign_asset_item(self, link):
        ag = AssetGUI(QFrame(), self)
        ag.assign_asset_item = QtWidgets.QFrame(self.ui.scrollAreaWidgetContents)
        ag.assign_asset_item.setObjectName("assign_asset_item")
        ag.indiviual_asset_container_layout_4 = QtWidgets.QHBoxLayout(ag.assign_asset_item)
        ag.indiviual_asset_container_layout_4.setObjectName("indiviual_asset_container_layout_4")
        ag.label_8 = QtWidgets.QLabel(ag.assign_asset_item)
        ag.label_8.setMaximumSize(QtCore.QSize(50, 16777215))
        ag.label_8.setObjectName("label_8")
        ag.indiviual_asset_container_layout_4.addWidget(ag.label_8)
        ag.my_id = QtWidgets.QLabel(ag.assign_asset_item)
        ag.my_id.setMinimumSize(QtCore.QSize(50, 0))
        ag.my_id.setMaximumSize(QtCore.QSize(200, 16777215))
        ag.my_id.setObjectName("my_id")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_id)

        ag.my_dia = QtWidgets.QLabel(ag.assign_asset_item)
        ag.my_dia.setMinimumSize(QtCore.QSize(50, 0))
        ag.my_dia.setMaximumSize(QtCore.QSize(200, 16777215))
        ag.my_dia.setObjectName("my_dia")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_dia)

        ag.my_dia_units = QtWidgets.QLabel(ag.assign_asset_item)
        ag.my_dia_units.setMinimumSize(QtCore.QSize(5, 0))
        ag.my_dia_units.setMaximumSize(QtCore.QSize(50, 16777215))
        ag.my_dia_units.setObjectName("my_dia_units")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_dia_units)

        ag.my_length = QtWidgets.QLabel(ag.assign_asset_item)
        ag.my_length.setMinimumSize(QtCore.QSize(50, 0))
        ag.my_length.setMaximumSize(QtCore.QSize(200, 16777215))
        ag.my_length.setObjectName("my_length")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_length)

        ag.my_length_units = QtWidgets.QLabel(ag.assign_asset_item)
        ag.my_length_units.setMinimumSize(QtCore.QSize(5, 0))
        ag.my_length_units.setMaximumSize(QtCore.QSize(50, 16777215))
        ag.my_length_units.setObjectName("my_length_units")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_length_units)

        ag.my_selected = QtWidgets.QCheckBox(ag.assign_asset_item)
        ag.my_selected.setObjectName("my_selected")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_selected)

        ag.label_9 = QtWidgets.QLabel(ag.assign_asset_item)
        ag.label_9.setObjectName("label_9")
        ag.indiviual_asset_container_layout_4.addWidget(ag.label_9)
        ag.my_group = QtWidgets.QComboBox(ag.assign_asset_item)
        ag.my_group.setMaximumSize(QtCore.QSize(100, 16777215))
        ag.my_group.setObjectName("my_group")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_group)
        # add label for Age
        ag.label_10 = QtWidgets.QLabel(ag.assign_asset_item)
        ag.label_10.setObjectName("label_10")
        ag.indiviual_asset_container_layout_4.addWidget(ag.label_10)
        ag.my_age = QtWidgets.QSpinBox(self.ui.groupBox)
        ag.my_age.setMaximum(999)
        ag.my_age.setObjectName("asset_age")
        ag.indiviual_asset_container_layout_4.addWidget(ag.my_age)
        spacerItem3 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        ag.indiviual_asset_container_layout_4.addItem(spacerItem3)
        self.ui.assign_asset_item_parent_layout.addWidget(ag.assign_asset_item)

        # set text
        _translate = QtCore.QCoreApplication.translate

        ag.label_8.setText(_translate("projectDataWidget", "ID: "))
        ag.my_id.setText(link.id)
        ag.my_dia.setText(str(link.diameter))
        ag.my_dia_units.setText(self.dunits)
        ag.my_length_units.setText(self.lunits)

        ag.my_length.setText(str(link.length))
        ag.label_9.setText(_translate("projectDataWidget", "Group"))
        ag.label_10.setText(_translate("projectDataWidget", "Age (y)"))

        # customize style
        ag.my_selected.setStyleSheet("""
                           /* other rules go here */
                           QCheckBox[selected="true"] {background-color: yellow};
                           QCheckBox[selected="false"] {background-color: palette(base)};
                            """)

        # add existing values of grouptocopy to my_group
        [ag.my_group.addItem(self.ui.grouptocopy.itemText(i))
         for i in range(self.ui.grouptocopy.count())]

        # add this to the record.
        # 1. Add _id to aq
        # 2. then add aq to the record
        ag.id_ = link.id
        ag.length_ = link.length
        ag.diameter_ = link.diameter
        self.add_plot_item_to_record(link.id, ag)

        # connect signal
        ag.my_selected.stateChanged.connect(self.myselectionchanged)
        ag.my_selected.stateChanged.connect(ag._selected_change_color)
        ag.my_group.currentIndexChanged.connect(ag.my_group_changed)
        ag.my_age.valueChanged.connect(ag.my_group_changed)

    def _getgroupname(self, i):
        return "G_%02d" % i

    def add_assetgroup(self, i, values=None):
        """values will be used as (A0, N0, age)"""

        ag = PropertyGroupGUI(frame=QFrame())
        ag.container_layout = QtWidgets.QHBoxLayout()
        ag.container_layout.setObjectName("assetgroup_container_layout")
        ag.no_label = QtWidgets.QLabel(self.ui.groupBox)
        ag.no_label.setObjectName("assetgroup_no_label")
        ag.container_layout.addWidget(ag.no_label)
        ag.A_label = QtWidgets.QLabel(self.ui.groupBox)
        ag.A_label.setObjectName("assetgroup_A_label")
        ag.container_layout.addWidget(ag.A_label)
        ag.A = QtWidgets.QLineEdit(self.ui.groupBox)
        ag.A.setMaximumSize(QtCore.QSize(50, 16777215))
        ag.A.setInputMask("")
        ag.A.setObjectName("assetgroup_A")
        ag.container_layout.addWidget(ag.A)
        ag.N0_label = QtWidgets.QLabel(self.ui.groupBox)
        ag.N0_label.setObjectName("assetgroup_N0_label")
        ag.container_layout.addWidget(ag.N0_label)
        ag.N0 = QtWidgets.QLineEdit(self.ui.groupBox)
        ag.N0.setMaximumSize(QtCore.QSize(50, 16777215))
        ag.N0.setInputMask("")
        ag.N0.setObjectName("assetgroup_N0")
        ag.container_layout.addWidget(ag.N0)
        ag.age_label = QtWidgets.QLabel(self.ui.groupBox)
        ag.age_label.setObjectName("assetgroup_age_label")
        ag.container_layout.addWidget(ag.age_label)
        # ag.age = QtWidgets.QSpinBox(self.ui.groupBox)
        # ag.age.setMaximum(999)
        # ag.age.setObjectName("assetgroup_age")
        # ag.container_layout.addWidget(ag.age)
        ag.spacer = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        ag.container_layout.addItem(ag.spacer)

        ag.frame.setLayout(ag.container_layout)
        self.ui.assetgroup_container_parent_layout.addWidget(ag.frame)

        _translate = QtCore.QCoreApplication.translate

        ag.no_label.setText(_translate("projectDataWidget", self._getgroupname(i)))
        ag.A_label.setText(_translate("projectDataWidget", "A"))
        ag.N0_label.setText(_translate("projectDataWidget", "N0"))
        # ag.age_label.setText(_translate("projectDataWidget", "Age"))

        # set defaults
        if(values):
            try:
                ag.A.setText(str(values[0]))
                ag.N0.setText(str(values[1]))
                # ag.age.setValue(int(values[2]))
            except Exception as e:
                logger = logging.getLogger()
                logger.exception("Error trying to set values with %s (Exception: %s)" % (values, e))
                values = None
        if(not values):
            ag.A.setText(str(c.DEFAULT_A))
            ag.N0.setText(str(c.DEFAULT_N0))
            # ag.age.setValue(int(c.DEFAULT_age))

        # Add validators

        ag.valNumber = QtGui.QDoubleValidator()
        ag.A.setValidator(ag.valNumber)
        ag.N0.setValidator(ag.valNumber)
        # ag.valInt=QtGui.QIntValidator()
        # ag.age.setValidator(ag.valInt)

        #
        self.assetgrouplist.append(ag)
        ag.A.textChanged.connect(self._validate_property_groups)
        ag.N0.textChanged.connect(self._validate_property_groups)
        # ag.age.valueChanged.connect(self._validate_property_groups)

    def _validate_property_groups(self, item=None):
        logger = logging.getLogger()
        logger.info("Validating property groups...")
        for group in self.assetgrouplist:
            try:
                float(group.A.text())
            except:
                group.A.setText(str(c.DEFAULT_A))
            try:
                float(group.N0.text())
            except:
                group.N0.setText(str(c.DEFAULT_N0))
            # try:
            #    int(group.age.text())
            # except:
            #    group.age.setValue(group.age.value())

    def get_active_groups(self):
        return [x for x in self.assetgrouplist if x.active]

    def closeEvent(self, evnt):
        evnt.ignore()
        self.setWindowState(QtCore.Qt.WindowMinimized)

    def keyPressEvent(self, e):
        if (e.key() != QtCore.Qt.Key_Escape):
            super(DataWindow, self).keyPressEvent(e)
        else:
            pass


class CurveDialogWithClosable(CurveDialog):

    """The mother dialog from which all the graph windows inherit from
       The constructor can send 'options' keyward argument containing a dict. Following entries are
       possible
                 title=None,
                 xlabel=None, ylabel=None, xunit=None, yunit=None,
                 section="plot", show_itemlist=False, gridparam=None,
                 curve_antialiasing=None


    """

    def __init__(self, *args, **kwargs):
        kwargs_ = dict(kwargs)
        del kwargs_["mainwindow"]
        self.mainwindow = kwargs["mainwindow"]
        super(CurveDialogWithClosable, self).__init__(*args, **kwargs_)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._can_be_closed = True
        self.get_plot().set_antialiasing(True)
        # self.add_tools()
        self.selected_holder = kwargs['mainwindow'].selected_holder
        self.enable_selection_update_signals()
        self.get_plot().SIG_ITEM_REMOVED.connect(self.__item_removed)
        self.myplotitems = {}

    def enable_selection_update_signals(self, set=True):
        if(set):
            self.get_plot().SIG_ITEM_SELECTION_CHANGED.connect(self.selected_holder)
            self.get_plot().SIG_ITEM_SELECTION_CHANGED.connect(self.select_siblings)
        else:
            self.get_plot().SIG_ITEM_SELECTION_CHANGED.disconnect()
            # self.get_plot().SIG_ITEM_SELECTION_CHANGED.connect(self.select_siblings)

    def select_siblings(self, widget):
        self.enable_selection_update_signals(False)  # temporariliy disable the signalling
        sel = [x for x in self.get_plot().get_selected_items() if hasattr(x, "id_")]
        items = [x for x in self.get_plot().get_items() if hasattr(x, "id_")]
        for item in sel:
            [self.get_plot().select_item(x) for x in items if x.id_ == item.id_]
        self.enable_selection_update_signals(True)  # now enable signalling

    def set_all_private(self):
        """" Set all current items in the plot private"""
        [x.set_private(True) for x in self.get_plot().get_items()]

    def set_axes_limits(self, axes_limits=None):
        """Sets axes limits axes_limits should be a list with four float values [x0,x1,y0,y1] """
        self.get_plot().PREFERRED_AXES_LIMITS = axes_limits
        # now autoscale
        self.get_plot().do_autoscale()
    
    def register_tools(self):
        from guiqwt.tools import ( SaveAsTool, CopyToClipboardTool, PrintTool, HelpTool, AntiAliasingTool, AxisScaleTool)
        logger=logging.getLogger()
        logger.info("Registering tools")
        self.add_tool(ResetZoomTool)
        self.register_standard_tools()
        # self.register_other_tools()
        self.add_tool(SaveAsTool)
        self.add_tool(CopyToClipboardTool)
        self.add_tool(PrintTool)
        self.add_tool(HelpTool)        
        # self.register_curve_tools()
        self.add_tool(AntiAliasingTool)
        self.add_tool(AxisScaleTool)    
        self.get_default_tool().activate()
        
    def register_standard_tools(self):
        """
        Registering basic tools for standard plot dialog
        --> top of the context-menu
        """
        from guiqwt.tools import ( SelectTool, RectZoomTool, BasePlotMenuTool, ExportItemDataTool, DisplayCoordsTool)
        t = self.add_tool(SelectTool)
        self.set_default_tool(t)
        self.add_tool(RectZoomTool)
        self.add_tool(BasePlotMenuTool, "item")
        self.add_tool(ExportItemDataTool)
        self.add_separator_tool()
        self.add_tool(BasePlotMenuTool, "grid")
        self.add_tool(BasePlotMenuTool, "axes")
        self.add_tool(DisplayCoordsTool)
        

    def setClosable(self, closable=True):
        self._can_be_closed = closable

    def closeEvent(self, evnt):
        if self._can_be_closed:
            super(CurveDialogWithClosable, self).closeEvent(evnt)

        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)

    def keyPressEvent(self, e):
        if (e.key() != QtCore.Qt.Key_Escape):
            super(CurveDialogWithClosable, self).keyPressEvent(e)
        else:
            pass

    def plot_item(self, id_, data, title="Point", icon="pipe.png"):
        raise NotImplemented

    def add_plot_item_to_record(self, id_, item):
        """All the plot items register here by calling this method. See also: remove_plot_item_from_record"""
        # TODO : DataWindow currently copies this function
        # need to implement multiple inheritance and make DRY
        self.myplotitems[id_] = item

    def remove_plot_item_from_record(self, id_):
        """When removing a plot item it should be notified to this function. See also: add_plot_item_to_record """
        # TODO : DataWindow currently copies this function
        # need to implement multiple inheritance and make DRY
        try:
            it = self.myplotitems[id_]
            del self.myplotitems[id_]
            return it
        except Exception:
            # that item is not with myplotitems, so, just ignore.
            logger = logging.getLogger()
            logger.exception("Exception at remove_plot_item_from_record")
            return None

    def __item_removed(self, goner):
        tmplist = dict(self.myplotitems)
        for id_, item in tmplist.items():
            if goner in item:
                # first remove related items.
                others = [x for x in item if x != goner]
                for i in others:
                    try:
                        self.get_plot().del_item(i)
                    except:
                        pass
                try:
                    self.remove_plot_item_from_record(id_)
                except:
                    pass


class RiskMatrix(CurveDialogWithClosable):

    def __init__(self, name="Risk Matrix", mainwindow=None, parent=None,
                 units=units["EURO"], options={}, axes_limits=[0, 15000, 0, 100]):
        if("xlabel" not in options):
            options['xlabel'] = "Consequence (%s)" % (units)
        if("ylabel" not in options):
            options['ylabel'] = "Proabability(-)"
        if("gridparam" not in options):
            options['gridparam'] = make.gridparam()

        super(RiskMatrix, self).__init__(edit=False,
                                         icon="risk.svg",
                                         toolbar=True,
                                         options=options,
                                         parent=parent,
                                         panels=None,
                                         wintitle=name,
                                         mainwindow=mainwindow)
        self.setClosable(False)
        self.set_axes_limits(axes_limits)

        l = make.legend("TR")
        self.get_plot().add_item(l)
        self.set_all_private()

    def set_axes_limits(self, axes_limits):
        _axes_limits = axes_limits[0], axes_limits[1] * 1.1, axes_limits[2], axes_limits[3] * 1.1
        super(RiskMatrix, self).set_axes_limits(_axes_limits)

    def get_ellipse_xaxis(self, consequence, probability):
        l = self.get_plot().PREFERRED_AXES_LIMITS
        SCALE = self.get_scale(consequence, probability, l)
        return consequence - SCALE, probability + SCALE,\
            consequence + SCALE, probability - SCALE

    def get_scale(self, consequence, probability, l):
        SC = self.mainwindow.projectgui.projectproperties.dataset.SCALE  # get the value on the dataset.
        SCALE = SC * math.pow(consequence * probability, .25) / math.pow((l[1] * l[3]), .25)
        return SCALE

    def set_proper_axis_limits(self):
        logger = logging.getLogger()
        try:
            v = self.myplotitems.values()
            all = [item for sublist in v for item in sublist]
            all = [x.get_center() for x in all if isinstance(x, EllipseShape)]
            a = array(all).T
            min_x = min(a[0])
            max_x = max(a[0])
            min_y = min(a[1])
            max_y = max(a[1])
            # min_y = min(a, axis=0)
            # max_x, max_y = max(a, axis=0)
            min_x = 0.0  # overrride
            tc = self.mainwindow.projectgui.projectproperties.dataset.totalcost
            max_x = max((tc * c.DIRECTCOSTMULTIPLIER, max_x))
            min_y = 0.0  # override
            # max_y = max((1, max_y))
            _axes_limits = [min_x, max_x, min_y, max_y]
            self.set_axes_limits(_axes_limits)
        except Exception:
            logger.exception("Error setting axis limits: ")

    def plot_links(self, links):
        logger = logging.getLogger()

        # we are plotting wholesale. So, disable signals temporily
        with u.updates_disabled_temporarily(self.get_plot()):
            if (not links):
                return
            if (not (hasattr(links[0], "cons") and hasattr(links[0], "prob"))):
                logger.info("The link does not have cons, prob attributes. Can not plot risk.")
                return
            # adfs = [x.cons for x in links]
            # prob = [x.prob for x in links]
            # first compute bounding box
            for link in links:
                self.plot_item(
                    id_=link.id,
                    data=[link.cons,
                          link.prob],
                    title="Point",
                    icon="pipe.png")

        self.set_proper_axis_limits()

    def replot_all(self):
        """Replots all items in myplotitems"""
        # self.set_proper_axis_limits()

        # we are plotting wholesale. So, disable signals temporily
        with u.updates_disabled_temporarily(self.get_plot()):

            for id_, item in self.myplotitems.items():
                self.plot_item(id_, [None, None])
            # now enable again

        # now set axis limits
        self.set_proper_axis_limits()

    def call_replot(self):
        """Calls replot() method of the default plot"""
        self.get_plot().replot()

    def plot_item(self, id_, data, title="Point", icon="pipe.png"):
        """Plot or update a plot"""
        global STYLE
        logger = logging.getLogger()
        # logger.info("Plotting : %s" % id_)
        consequence, probability = data
        if (consequence is None):
            try:
                # logger.info("No value provided for consequence, trying existing value.")
                consequence = self.myplotitems[id_][0].get_center()[0]
            except:
                logger.info(
                    "trying to get consequence from previous plot.. that failed too. give up.")
                return
        if (probability is None):
            try:
                # logger.info("No value provided for probability, trying existing value.")
                probability = self.myplotitems[id_][0].get_center()[1]
            except:
                logger.info(
                    "trying to get probability from previous plot.. that failed too. give up.")
                return

        try:
            v = self.myplotitems[id_]
            # for item in v:  # then remove from plots
            #    self.get_plot().removeItem(
            # item)  # this will automatically call remove_plot_item_from_record
            # and remove it from myplotitems

            # just change the diameter and origin of ellipse and move the label
            v[0].set_xdiameter(*self.get_ellipse_xaxis(consequence, probability))
            v[1].set_pos(consequence, probability)

        except KeyError:  # the item is not in myplotitems
            ci = make.ellipse(*self.get_ellipse_xaxis(consequence, probability),
                              title=title)
            ci.shapeparam._DataSet__icon = u.get_icon('Risk')
            ci.shapeparam._DataSet__title = title
            param = ci.shapeparam
            param.fill.color = QColor('red')
            param.sel_fill.color = QColor('purple')
            param.sel_fill.alpha = .7
            param.sel_symbol.Marker = "NoSymbol"
            param.sel_symbol.Color = QColor('red')
            update_style_attr('-r', param)
            param.update_shape(ci)
            ci.id_ = id_  # add the id to the item before plotting.
            self.get_plot().add_item(ci)
            # now add a label with link id
            la = make.label(id_, ci.get_center(), (0, 0), "C")
            la.id_ = id_  # add the id to the item before plotting.
            self.get_plot().add_item(la)
            la.set_private(False)
            self.add_plot_item_to_record(id_, [ci, la])


class NetworkMap(CurveDialogWithClosable):

    def __init__(self, name="Network Map", mainwindow=None,
                 nodes=None, links=None, parent=None, options={}):
        if("xlabel" not in options):
            options['xlabel'] = "X (distance units)"
        if("ylabel" not in options):
            options['ylabel'] = "Y (distance units)"

        gridparam = make.gridparam()

        super(NetworkMap, self).__init__(edit=False,
                                         icon="network.svg",
                                         toolbar=True,
                                         options=dict(gridparam=gridparam),
                                         parent=parent,
                                         wintitle=name,
                                         panels=None,
                                         mainwindow=mainwindow)
        self.setClosable(False)

        # legend = make.legend("TR")
        # self.get_plot().add_item(legend)
        self.set_all_private()
        self.draw_network(nodes, links)

    def draw_network(self, nodes, links):
        app = QApplication.instance()
        logger = logging.getLogger()
        # we are plotting wholesale. So, disable signals temporily
        with u.updates_disabled_temporarily(self.get_plot()):

            if(nodes):
                logger.info("Drawing nodes")
                app.processEvents()
                self.draw_nodes(nodes)
            # we don't want users to select grid, or nodes and they should not appear in the item list.
            # So lock'em up.
            self.set_all_private()

            if(links):
                logger.info("Drawing links")
                app.processEvents()
                self.draw_links(links)
        self.get_plot().do_autoscale(replot=True)

    def interp_curve(self, x, y):
        # how many points in the line (say max is 5)
        DELTA = .01
        t = arange(len(x))
        t_ = arange(0, len(x) - 1 + DELTA, DELTA)
        x_ = interp(t_, t, x)
        y_ = interp(t_, t, y)

        return x_, y_

    def draw_links(self, links):
        for link in links:
            pts = [(link.start.x, link.start.y)] + link.vertices + [(link.end.x, link.end.y)]
            title = u.get_title(link)
            icon = u.get_icon(link)
            id_ = link.id
            self.plot_item(id_, pts, title, icon)

    def plot_item(self, id_, data, title, icon="pipe.png"):
        x = [n[0] for n in data]
        y = [n[1] for n in data]
        x_, y_ = self.interp_curve(x, y)
        cu = make.curve(x_, y_, title=title)
        cu.curveparam._DataSet__icon = icon
        cu.curveparam._DataSet__title = title
        cu.id_ = id_  # add the ide to the item before plotting.
        self.get_plot().add_item(cu)

        # create a label for the node and add it to the plot
        l = int(len(x_) / 2.0)
        la = make.label(id_, (x_[l], y_[l]), (0, 0), "C")
        la.id_ = id_
        la.set_private(True)
        self.get_plot().add_item(la)
        la.set_private(True)

        self.add_plot_item_to_record(id_, [cu, la])

    def draw_nodes(self, nodes):

        for node in nodes:
            cu = make.curve([node.x, node.x], [node.y, node.y],
                            # ^ this is a hack. gwiqwt curve has problems when constructed with single coordinae
                            title=u.get_title(node), marker="Ellipse", curvestyle="NoCurve")
            cu.set_selectable(False)
            cu.set_private(True)
            # pt=make.ellipse(node.x-.1,node.y-.1,node.x+.1,node.y+.1)
            # pt=PointShape(x=node.x,y=node.y, color="g")
            cu.curveparam._DataSet__icon = u.get_icon(node)
            cu.curveparam._DataSet__title = u.get_title(node)
            self.get_plot().add_item(cu)

            # create a label for the node and add it to the plot
            la = make.label(node.id, (node.x, node.y), (0, 0), "TL")
            la.set_private(True)
            self.get_plot().add_item(la)


class optimalTimeGraph(CurveDialogWithClosable):

    def __init__(self, name="Whole life cost", mainwindow=None, year=None,
                 damagecost=None, renewalcost=None, units=units["EURO"],
                 parent=None, options={}):
        self.mainwindow = mainwindow
        if("xlabel" not in options):
            options['xlabel'] = "Time(years)"
        if("ylabel" not in options):
            options['ylabel'] = "Cost (%s)" % (units)

        self.curvesets = []

        super(optimalTimeGraph, self).__init__(edit=False,
                                               icon="wlc.svg",
                                               toolbar=True,
                                               options=options,
                                               parent=parent,
                                               panels=None,
                                               wintitle=name,
                                               mainwindow=mainwindow)

        if (isinstance(self.mainwindow, MainWindow)):
            self.mainwindow.optimaltimegraphs[id(self)] = self

        legend = make.legend("TR")
        self.get_plot().add_item(legend)
        if(year is None or damagecost is None or renewalcost is None):
            pass
        else:
            self.plotCurveSet(name, year, damagecost, renewalcost)
            
    def _plot_selected_items(self):
        """Plots the assets that are currently selected in other windows with this plot. """
        logger=logging.getLogger()
        logger.info("** Not implemented _plot_selected_items ")        
            
    def register_tools(self):
        logger=logging.getLogger()
        logger.info("Registering WLC tool")
        self.add_separator_tool()
        self.add_tool(PlotWLCTool)
        super(optimalTimeGraph,self).register_tools()
        
    def closeEvent(self, evnt):
        if (not isinstance(self.mainwindow, MainWindow)):
            _can_be_closed = True
        elif (len(self.mainwindow.optimaltimegraphs) > 1):
            _can_be_closed = True
            del(self.mainwindow.optimaltimegraphs[id(self)])
        else:
            _can_be_closed = False

        if _can_be_closed:
            super(optimalTimeGraph, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)

    def plot_item(self, id_, data, title, icon="pipe.png"):
        year, damagecost, renewalcost = data
        self.add_plot_item_to_record(id_, self.plotCurveSet(title, year, damagecost, renewalcost))

    def plotCurveSet(self, id_, year, damagecost, renewalcost):
        c = curve_colors[len(self.curvesets) % len(curve_colors)]
        dc = make.curve(
            year, damagecost, title="Damage Cost", color=c, linestyle="DashLine",
            linewidth=3, marker=None,
            markersize=None,
            markerfacecolor=None,
            markeredgecolor=None, shade=None,
            curvestyle=None, baseline=None,
            xaxis="bottom", yaxis="left")
        dc.id_ = id_  # add the ide to the item before plotting.
        self.get_plot().add_item(dc)
        rc = make.curve(
            year, renewalcost, title="Renewal Cost", color=c, linestyle="DotLine",
            linewidth=3, marker=None,
            markersize=None,
            markerfacecolor=None,
            markeredgecolor=None, shade=None,
            curvestyle=None, baseline=None,
            xaxis="bottom", yaxis="left")
        rc.id_ = id_  # add the ide to the item before plotting.
        self.get_plot().add_item(rc)
        tc = make.curve(
            year, array(damagecost) + array(renewalcost), title="Total Cost", color=c, linestyle=None,
            linewidth=5, marker=None,
            markersize=None,
            markerfacecolor=None,
            markeredgecolor=None, shade=None,
            curvestyle="Lines", baseline=None,
            xaxis="bottom", yaxis="left")
        tc.id_ = id_  # add the ide to the item before plotting.
        self.get_plot().add_item(tc)
        self.curvesets.append([id_, dc, tc, rc])
        return [dc, tc, rc]


class MainWindow(QMainWindow):

    """The maion 'container' of the application. This is a multi-document interface where all other
    windows live in."""

    class MenuItems:
        pass
    menuitems = MenuItems
    menuitems.file = "&File"
    menuitems.view = "&View"
    menuitems.new_wlc = "New &WLC window"
    menuitems.cascade = "&Cascade"
    menuitems.tiled = "&Tiled"
    menuitems.show_log = "Show &Log"
    menuitems.new_project = "&New Project"
    menuitems.open_project = "&Open project"
    menuitems.save_project_as = "Save Project &As"
    menuitems.save_project = "&Save Project"

    menuitems.close_project = "&Close Project"

    update_selected_items = True
    LOGSTARTMESSAGE = "Logging started"

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self._setup_logging()
        self.LASTPROJECT = None
        self.EPANETLOC = None
        self.projectgui = rrpam_wds.gui.subdialogs.ProjectGUI(self)
        self.mdi = QMdiArea()
        self.arrange_properties_panel()
        self.setMenu()
        self.connect_project_manager()
        self._initialize_all_components()
        self._create_progressbar()
        self._manage_window_settings()

    @pyqtSlot(object)
    def _progressbar_set(self, set_):
        self._progressbar_set_(set_)

    def _progressbar_set_(self, set_):
        logger = logging.getLogger()
        if(set_):
            logger.info("** I got message - calculation started")
            self.progressbar.exec_()
        else:
            logger.info("** I got message - calculation ENDED")
            self.progressbar.close()

    def _create_progressbar(self):
        self.progressbar = rrpam_wds.gui.subdialogs.ProgressBar(
            parent=self,
            flags=0,
            message="Doing Hydraulic Calculations")
        self.pm.i_start_calculations.connect(self._progressbar_set)
        # self.pm.heres_a_project_signal.connect(self._progressbar_set)

    def _initialize_all_components(self):
        self._delete_all_subwindows()
        self._standard_windows()

    def _delete_all_subwindows(self):
        # let's close all existing subwindows.
        self._remove_all_subwindows()
        self.datawindow = None
        self.networkmap = None
        self.riskmatrix = None

    def arrange_properties_panel(self):
        self.qs = QSplitter(self)
        self.frame = QFrame(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.projectgui.projectproperties)
        layout.insertStretch(1)
        self.frame.setLayout(layout)
        self.qs.addWidget(self.frame)
        for x in self.projectgui.projectproperties.findChildren(QSlider):
            x.setMinimumWidth(100)

        self.qs.addWidget(self.mdi)
        self.setCentralWidget(self.qs)

    def _manage_window_settings(self, save=False):
        """ if (save=False) At application initialization, will set the application GUI geometry and components
        from  values saved at the end of the previous session.

        Otherwise (save=True) it will
        """
        QApplication.setOrganizationName("AsselaPathirana")
        QApplication.setOrganizationDomain("assela.pathirana.net")
        QApplication.setApplicationName("RRPAMWDS")
        settings = QtCore.QSettings()

        if(save):
            settings.beginGroup("MainWindow")
            settings.setValue("size", self.size())
            settings.setValue("pos", self.pos())
            settings.endGroup()

            settings.beginGroup("DataWindow")
            settings.setValue("size", self.datawindow.parent().size())
            settings.setValue("pos", self.datawindow.parent().pos())
            settings.endGroup()

            settings.beginGroup("RiskPlot")
            settings.setValue("size", self.riskmatrix.parent().size())
            settings.setValue("pos", self.riskmatrix.parent().pos())
            settings.endGroup()

            settings.beginGroup("NetworkMap")
            settings.setValue("size", self.networkmap.parent().size())
            settings.setValue("pos", self.networkmap.parent().pos())
            settings.endGroup()

            settings.beginGroup("optimal_time_graphs")
            settings.setValue("size", self.get_optimal_time_graphs()[0].parent().size())
            settings.setValue("pos", self.get_optimal_time_graphs()[0].parent().pos())
            settings.endGroup()

            settings.beginGroup("last_project")
            settings.setValue("LASTPROJECT", self.LASTPROJECT)
            settings.setValue("EPANETLOC", self.EPANETLOC)
            settings.endGroup()

        else:

            settings.beginGroup("MainWindow")
            self.resize(settings.value("size", QtCore.QSize(400, 400), type=QtCore.QSize))
            self.move(settings.value("pos", QtCore.QPoint(200, 200), type=QtCore.QPoint))
            settings.endGroup()

            settings.beginGroup("DataWindow")
            self.datawindow.parent().resize(
                settings.value("size", QtCore.QSize(400, 400), type=QtCore.QSize))
            self.datawindow.parent().move(
                settings.value("pos", QtCore.QPoint(200, 200), type=QtCore.QPoint))
            settings.endGroup()

            settings.beginGroup("RiskPlot")
            self.riskmatrix.parent().resize(
                settings.value("size", QtCore.QSize(400, 400), type=QtCore.QSize))
            self.riskmatrix.parent().move(
                settings.value("pos", QtCore.QPoint(100, 100), type=QtCore.QPoint))
            settings.endGroup()

            settings.beginGroup("NetworkMap")
            self.networkmap.parent().resize(
                settings.value("size", QtCore.QSize(400, 400), type=QtCore.QSize))
            self.networkmap.parent().move(
                settings.value("pos", QtCore.QPoint(100, 100), type=QtCore.QPoint))
            settings.endGroup()

            settings.beginGroup("optimal_time_graphs")
            self.get_optimal_time_graphs()[0].parent().resize(
                settings.value("size", QtCore.QSize(400, 400), type=QtCore.QSize))
            self.get_optimal_time_graphs()[0].parent().move(
                settings.value("pos", QtCore.QPoint(100, 100), type=QtCore.QPoint))
            settings.endGroup()

            settings.beginGroup("last_project")
            self.LASTPROJECT = settings.value("LASTPROJECT", None, type=str)
            self.EPANETLOC = settings.value("EPANETLOC", None, type=str)
            settings.endGroup()

    def closeEvent(self, event):
        self._manage_window_settings(save=True)
        rrpam_wds.config.save()
        event.accept()

    def _setup_logging(self):
        setup_logging()
        logger = logging.getLogger()
        handler = [x for x in logger.handlers if isinstance(x, EmittingLogger)][0]
        self.logdialog = LogDialog(parent=self)
        handler.logsender.logsender_signal.connect(self.logdialog.reciever)
        logger.info(self.LOGSTARTMESSAGE)

    def hide_log_window(self):
        self.logdialog.setVisible(False)
        logmdi = [x for x in self.mdi.subWindowList() if isinstance(x.widget(), LogDialog)][0]
        logmdi.setVisible(False)

    def show_logwindow(self):
        self._setup_logging()
        if(not any([x for x in self.mdi.subWindowList() if isinstance(x.widget(), LogDialog)])):
            self.addSubWindow(self.logdialog)
        self.logdialog.setVisible(True)

    def connect_project_manager(self):
        self.pm = PM(self.projectgui.projectproperties.dataset)
        self.projectgui._new_project_signal.connect(self.pm.new_project)
        self.pm.heres_a_project_signal.connect(self.take_up_results)

    def _remove_all_subwindows(self):
        for subw in self.mdi.subWindowList():
            widget = subw.widget()
            subw.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            subw.close()
            widget.close()
            widget.setParent(None)
            subw.setParent(None)
            widget.deleteLater()
            subw.deleteLater()

    def _standard_windows(self):
        self.add_datawindow()
        self.add_networkmap()
        self.add_riskmatrix()
        self.optimaltimegraphs = {}
        self.add_optimaltimegraph()
        self._manage_window_settings()

    def selected_holder(self, widget):
        """ When mocking remember do not patch slots. This is a slot. So, instead patch the function this calls below. """
        logger = logging.getLogger()
        logger.info("Got message of change from: %s" % widget)
        if(self.update_selected_items):
            logger.info("Responding...")
            self.update_all_plots_with_selection(widget)
        else:
            logger.info("Ignoring...")

    def update_all_plots_with_selection(self, widget):
        logger = logging.getLogger()
        logger.info("selection changed!")
        # first switch off responding to selections
        self.update_selected_items = False
        try:
            # firt get all subplots
            subplots = [x.get_plot() for x in self.optimaltimegraphs.values()]
            subplots.append(self.riskmatrix.get_plot())
            subplots.append(self.networkmap.get_plot())
            subplots.append(self.datawindow.get_plot())
            # OK, now remove the plot represented by the argument 'widget'
            subplots = filter(lambda a: a != widget, subplots)
            # now select the selections of 'widget' in them.
            selected_ids = [x.id_ for x in widget.get_selected_items()]
            for p in subplots:
                # if p is dataWindow, do not
                # find corressponding items
                targets = [x for x in p.get_items() if getattr(x, 'id_', None) in selected_ids]
                # now update
                with u.updates_disabled_temporarily(p):
                    p.select_some_items(targets)

        except Exception as e:
            logger = logging.getLogger()
            logger.exception("non selectable item! (%s)" % e)
        # don't forget to reset
        self.update_selected_items = True

    def get_optimal_time_graphs(self):
        """returnas a list of optimaltimegraphs"""
        return list(self.optimaltimegraphs.values())

    def add_optimaltimegraph(self):
        wlc = optimalTimeGraph(mainwindow=self)
        self.mdi.addSubWindow(wlc)
        wlc.show()

    def add_datawindow(self):
        if(not any([x for x in self.mdi.subWindowList() if isinstance(x.widget(), DataWindow)])):
            self.datawindow = DataWindow(mainwindow=self, parent=self.mdi)
            self.mdi.addSubWindow(self.datawindow)
            self.datawindow.show()

    def add_riskmatrix(self):
        if(not any([x for x in self.mdi.subWindowList() if isinstance(x.widget(), RiskMatrix)])):
            self.riskmatrix = RiskMatrix(mainwindow=self)
            self.mdi.addSubWindow(self.riskmatrix)
            self.riskmatrix.show()

    def add_networkmap(self):
        if(not any([x for x in self.mdi.subWindowList() if isinstance(x.widget(), NetworkMap)])):
            self.networkmap = NetworkMap("Network Map", mainwindow=self)
            self.mdi.addSubWindow(self.networkmap)
            self.networkmap.show()

    def setMenu(self):
        bar = self.menuBar()
        bar.setNativeMenuBar(False)  # disable different treatment in Mac OS
        file = bar.addMenu(self.menuitems.file)
        file.addAction(self.menuitems.new_project)
        file.addAction(self.menuitems.save_project)
        file.addAction(self.menuitems.save_project_as)
        file.addAction(self.menuitems.open_project)
        file.addAction(self.menuitems.new_wlc)
        file.addAction(self.menuitems.show_log)
        file.addAction(self.menuitems.close_project)
        file.triggered[QAction].connect(self.windowaction)
        file2 = bar.addMenu(self.menuitems.view)
        file2.addAction(self.menuitems.cascade)
        file2.addAction(self.menuitems.tiled)
        file2.triggered[QAction].connect(self.windowaction)

    def windowaction(self, q):
        logger = logging.getLogger()
        logger.info("Menu: %s" % q.text())

        if q.text() == self.menuitems.new_wlc:
            self.add_optimaltimegraph()

        if q.text() == self.menuitems.cascade:
            self.mdi.cascadeSubWindows()

        if q.text() == self.menuitems.tiled:
            self.mdi.tileSubWindows()

        if q.text() == self.menuitems.show_log:
            self.show_logwindow()

        if q.text() == self.menuitems.new_project:
            self._new_project()

        if q.text() == self.menuitems.open_project:
            self._open_project()

        if q.text() == self.menuitems.save_project:
            self._save_project()

        if q.text() == self.menuitems.save_project_as:
            self._save_project_as()

        if q.text() == self.menuitems.close_project:
            self.projectgui.close_project()

    def _save_project(self):
        self.projectgui.save_project()

    def _save_project_as(self):
        self.projectgui.save_project_as()

    def _new_project(self):
        self.projectgui.new_project()

    def _open_project(self):
        """Opening a project"""
        self.projectgui.open_project()

    @pyqtSlot(object)
    def take_up_results(self, results):
        """Will display the items represented in the project."""

        logger = logging.getLogger()
        logger.info("I got it!")
        # first update this in project properties
        self.projectgui.projectproperties.dataset.set_network(results)
        self._display_project(results)

    def _display_project(self, results=None):
        self._initialize_all_components()
        if (not results):
            results = self.projectgui.projectproperties.dataset.get_network()
        nodes = getattr(results, "nodes", None)
        links = getattr(results, "links", None)
        self.networkmap.draw_network(nodes, links)
        app = QApplication.instance()
        app.processEvents()
        self.datawindow.draw_network(links)
        app.processEvents()
        links = self._calculate_risk(links)
        app.processEvents()
        self.riskmatrix.plot_links(links)
        app.processEvents()

    def assets_group_changed_reciever(self, id_):
        logger = logging.getLogger()
        logger.info("** I got it.")
        if (len(self.riskmatrix.myplotitems) > 0):
            data = [None, self.datawindow.getProb(id_, 0)]
            self.riskmatrix.plot_item(id_, data)
            self.riskmatrix.set_proper_axis_limits()
            self.riskmatrix.call_replot()

    def _calculate_risk(self, links):
        logger = logging.getLogger()
        if (not links):
            return
        for link in links:
            if (not hasattr(link, 'ADF')):
                logger.info("No ADF value. I can not calcualte risk components")
                continue
            link.prob = self.datawindow.getProb(link.id, 0)  # 0 means now.
            link.cons = (1. - link.ADF) * \
                self.projectgui.projectproperties.dataset.totalcost * \
                c.DIRECTCOSTMULTIPLIER
        return links

    def addSubWindow(self, *args, **kwargs):
        self.mdi.addSubWindow(*args, **kwargs)


def main():  # pragma: no cover
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
