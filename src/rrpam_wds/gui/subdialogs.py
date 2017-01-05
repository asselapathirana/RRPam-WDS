from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA

import logging
import os
import pickle as pickle
import shutil

import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt
from guidata.dataset.qtwidgets import DataSetEditGroupBox
from guidata.hdf5io import HDF5Reader
from guidata.hdf5io import HDF5Writer
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QVBoxLayout

import rrpam_wds.constants as c
import rrpam_wds.gui.dialogs
from rrpam_wds.constants import ResultSet


class ProgressBar(QDialog):

    def __init__(self, parent=None, flags=None, message=None):
        self.message = message
        if (not flags):
            flags = Qt.FramelessWindowHint
        super(ProgressBar, self).__init__(parent=parent, flags=flags)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        lab = QLabel(message, self)
        vbox.addWidget(lab)
        pb = QProgressBar()
        pb.setRange(0, 0)
        vbox.addWidget(pb)
        self.setLayout(vbox)


class ProjectGUI(QObject):
    logger = logging.getLogger()
    _new_project_signal = pyqtSignal()

    def __init__(self, parent):
        super(ProjectGUI, self).__init__()
        self.parent = parent
        self.projectproperties = DataSetEditGroupBox(
            "title",
            ProjectPropertiesDataset,
            comment="foox")
        self.projectproperties.SIG_APPLY_BUTTON_CLICKED.connect(self._apply_dataset_values)

    def _apply_dataset_values(self):
        """This is connected to a signal. When mocking, use apply_dataset_values method."""
        self.logger.info("Me pressed.")
        self.apply_dataset_values()

    def apply_dataset_values(self):
        self.parent.riskmatrix.replot_all()

    def check_epanetfile(self, enfile):
        if(os.path.isfile(enfile)):
            self.logger.info("EPANET valid file check. To be implemented")
            return enfile
        else:
            self.logger.info("Not a valid epanetfile: %s" % enfile)
            msgBox = QMessageBox(parent=self.parent)
            msgBox.setText("This is not a valid epanet file")
            msgBox.exec_()
            return None

    def log(self):
        try:
            k = self.projectproperties.dataset
            self.logger.info("discount rate =%s" % (k.discountrate))
        except Exception:
            pass

    def rewrite_values_in_gui_with_variables(self):
        self.logger.info("Writing: var>GUI ")
        self.log()
        self.projectproperties.get()

    def rewrite_values_in_variables_with_gui(self):
        self.logger.info("Writing: GUI>var ")
        self.log()
        # disable events from firing
        __status = self.projectproperties.blockSignals(True)
        self.projectproperties.set()
        # now enable them again
        self.projectproperties.blockSignals(__status)

    def new_project(self):
        self.logger.info("New Project")
        # first step, get the name of the epanet file from the user.
        if(self._new_project()):
            # now we inform the project_manager to do the calculation
            self._new_project_signal.emit()

    def _new_project(self):
        epanetfile, filter = self._getSaveFileName2(self.parent,
                                                    "Select a valid EPANET 2.0 network file",
                                                    self.parent.EPANETLOC or c.HOMEDIR,
                                                    filter='*.inp')

        epanetfile = self.check_epanetfile(epanetfile)
        if(not epanetfile):
            return False
        msg = "New Project"
        self.projectproperties.dataset.projectname = self._create_empty_project(msg, epanetfile)
        self.parent.LASTPROJECT = self.projectproperties.dataset.projectname
        self.parent.EPANETLOC = os.path.dirname(epanetfile)
        self.rewrite_values_in_gui_with_variables()
        return True

    def _getSaveFileName(self, *args, **kwargs):
        # why this function and _getSaveFileName2? for tests to mock this method easily.
        self.logger.info("proxy calling QFileDialog.getSaveFileName ")
        return QFileDialog.getSaveFileName(*args, **kwargs)

    def _getSaveFileName2(self, *args, **kwargs):
        # why this function and _getSaveFileName? for tests to mock this method easily.
        self.logger.info("proxy calling QFileDialog.getOpenFileName ")
        return QFileDialog.getOpenFileName(*args, **kwargs)

    def _getOpenFileName(self, *args, **kwargs):
        self.logger.info("proxy calling QFileDialog.getOpenFileName ")
        return QFileDialog.getOpenFileName(*args, **kwargs)

    def _create_empty_project(self, msg, epanetfile):
        projectfile = self.get_save_filename(msg)
        self.logger.info(
            "creating empty project with filename %s and epanetfile %s " %
            (projectfile, epanetfile))
        if(not projectfile):
            return None
        else:
            return self._save_project_to_dest(projectfile, epanetfile=epanetfile)

    def get_save_filename(self, msg):
        projectfile, filter = self._getSaveFileName(self.parent,
                                                    msg,
                                                    self.parent.LASTPROJECT or c.HOMEDIR,
                                                    filter='*' + c.PROJECTEXTENSION)
        self.logger.info("Selected file for save/new project : %s " % projectfile)
        return projectfile

    def _update_results_with_gui_values(self):
        """Update the self.projectproperties.dataset.results object with
        group information. Call this before pickling data"""
        r = self.projectproperties.dataset.results
        if(not r):
            self.logger.info("No results available yet with projectproperties. So, not updating")
        else:
            self.logger.info("Updating projectproperties.dataset.results with my_group")
            for item in r.links:
                item.asset_group = self.parent.datawindow.get_asset_group(item.id)
                item.age = self.parent.datawindow.get_age(item.id)

    def _save_project_to_dest(self, projectfile, epanetfile=None):

        self.logger.info("Getting values from datawindow..")
        # First get latest values from dataWindow
        inf = self.parent.datawindow.get_information(all=True)
        self.projectproperties.dataset.group_list_to_save_or_load = inf
        self._update_results_with_gui_values()
        self.logger.info("Now writing data")
        prjname, subdir, ext = c._get_dir_and_extention(projectfile)
        self.projectproperties.dataset.write_data(prjname)

        if(not os.path.isdir(subdir)):
            os.mkdir(subdir)
            self.logger.info("Created  directory %s" % subdir)

        if(epanetfile):
            base = os.path.basename(epanetfile)
            dst = os.path.join(os.path.dirname(prjname), base)
            shutil.copy(epanetfile, dst)
            self.projectproperties.dataset.fname = base
            self.logger.info("copied epanet file to %s" % dst)
        return prjname

    def try_loading_project_properties(self, prj):
        try:
            self.logger.info("Trying to read properties from %s " % prj)
            if(self.projectproperties.dataset.read_data(prj)):
                self.logger.info(" %s project read successfully." % prj)
                return True
        except Exception as e:
            self.logger.exception("Could not load the project properties: %s" % e)
        return False

    def save_project(self):
        self.logger.info("Saving the project")
        # Implement the actions needed to save the project here.
        # first update any user changes in parameters
        self.rewrite_values_in_variables_with_gui()
        try:
            self._save_project_to_dest(self.projectproperties.dataset.projectname)
        except Exception as e:
            self.logger.exception("Exception %s " % e)

    def save_project_as(self):
        msg = "Save project as"
        self.projectproperties.dataset.projectname = self.get_save_filename(msg)
        self.save_project()

    def open_project(self):
        while (True):
            projectfile, filter = self._getOpenFileName(self.parent,
                                                        "Open project",
                                                        self.parent.LASTPROJECT or c.HOMEDIR,
                                                        filter='*' + c.PROJECTEXTENSION)
            if(not projectfile):
                return None
            projectfile, dir, ext = c._get_dir_and_extention(projectfile)
            self.logger.info("Selected file to open : %s " % projectfile)
            # check if it is a valid project
            if(self._valid_project(projectfile)):
                self.projectproperties.dataset.projectname = projectfile
                self.parent.LASTPROJECT = self.projectproperties.dataset.projectname
                self.parent._display_project()
                # now update the dataWindow with project groups in opened project
                self.parent.datawindow.set_information(
                    self.projectproperties.dataset.group_list_to_save_or_load)
                self.logger.info("Updated dataWindow with project groups")
                # since we have done both (a) displaying network and
                # (b) updating the asset groups, now we can assign correct asset group
                # to each asset item
                if(self.projectproperties.dataset.results):
                    r = self.projectproperties.dataset.results.links
                    self.parent.datawindow.assign_values_to_asset_items(r)
                break
            else:
                self.logger.info("Project loading failed: Not a valid project")
                return None

        self.logger.info("Open Project valid")
        self.rewrite_values_in_gui_with_variables()
        self.apply_dataset_values()
        return (projectfile)

    def _valid_project(self, prj):
        """Check if prj represents a valid project. """
        if (not os.path.isfile(prj)):
            return False
        if (not os.path.isdir(c._get_dir_and_extention(prj)[1])):
            return False
        # Try opening
        self.logger.info("Now calling try_loading_project_properties ")
        return self.try_loading_project_properties(prj)

    def close_project(self):
        self.logger.info("Close Project")


class ProjectPropertiesDataset(dt.DataSet):

    """Project : """
    _bg4 = dt.BeginGroup("Project")
    projectname = di.StringItem("", help="Project path").set_prop("display", active=False)
    _eg4 = dt.EndGroup("Project")
    _bg3 = dt.BeginGroup("Epanet file of this project")
    fname = di.StringItem("", help="Epanet file of this project").set_prop("display", active=False)
    _eg3 = dt.EndGroup("Epanet file of this project")
    _bg5 = dt.BeginGroup("Units")
    lunits = di.StringItem("Length  : ", help="Length units").set_prop("display", active=False)
    dunits = di.StringItem("Diameter: ", help="Diameter units").set_prop("display", active=False)
    _eg5 = dt.EndGroup("Epanet file of this project")
    di.FileOpenItem("Select Epanet file (open)", ("inp", "eta"))
    _bx1 = dt.BeginGroup("Direct cost total system down")
    totalcost = di.FloatItem(
        "(x%d %s)" % (c.DIRECTCOSTMULTIPLIER,
                      c.units['EURO']),
        default=10,
        min=0,
        step=1,
        slider=False)
    _ex1 = dt.EndGroup("Direct cost total system down")
    _bx2 = dt.BeginGroup("Relative size in risk matrix")
    SCALE = di.FloatItem("", default=10, min=0.0, max=+500, step=.1, slider=True)
    _ex2 = dt.EndGroup("Relative size in risk matrix")
    _bg2 = dt.BeginGroup("Discount rate (%)")
    discountrate = di.FloatItem("", default=10, min=-5, max=+50, step=0.1, slider=True)
    _eg2 = dt.EndGroup("Discount rate (%)")
    _bg8 = dt.BeginGroup("Time Horizon (years)")
    timehorizon = di.FloatItem("", default=20, min=1, max=+200, step=1, slider=True)
    _eg8 = dt.EndGroup("Time Horizon (years)")

    def __init__(self, title=None, comment=None, icon=''):
        self.logger = logging.getLogger()
        self.results = None
        super(ProjectPropertiesDataset, self).__init__(title, comment, icon)

    # def show(self):
    #    return self.edit()
    def get_nwstore_file(self, f):
        return os.path.join(c._get_dir_and_extention(f)[1], "network." + "__")

    def get_assetgroups_file(self, f):
        return os.path.join(c._get_dir_and_extention(f)[1], "assetgroups." + "__")

    def read_data(self, projfile):
        if os.path.exists(projfile):
            try:
                self.logger.info("Reading HDF 5 data from %s" % projfile)
                reader = HDF5Reader(projfile)
                self.deserialize(reader)
                try:
                    self.logger.info("Read discountrate=%s" % self.discountrate)
                except AttributeError:
                    pass
                reader.close

            except:
                self.logger.info("Exception with HDF reader for file %s" % projfile)
                return False

            if (not self._read_network_data(projfile)):
                return False

            if (not self._read_asset_group_data(projfile)):
                return False
            return True
        else:
            return False

    def _read_asset_group_data(self, projfile):
        f = self.get_assetgroups_file(projfile)
        try:
            with open(f, 'rb') as stream:
                self.logger.info("Reading results  from %s" % f)
                self.group_list_to_save_or_load = pickle.load(stream)
                l = self.group_list_to_save_or_load
                self.logger.info("read %d items, list: %s" % (len(l), l))
        except Exception as e:
                self.logger.info("Exception reading saved results %s, %s" % (projfile, e))
                return False
        return True

    def _set_units(self):
        self.logger.info("READING UNITS ...")
        if(self.results):
            self.lunits, self.dunits = c.units[self.results.units]
        else:
            self.logger.exception("WARNING: Empty result set!!")

    def _read_network_data(self, projfile):
        f = self.get_nwstore_file(projfile)

        try:
            with open(f, 'rb') as stream:
                self.logger.info("Reading results  from %s" % f)
                self.results = pickle.load(stream)
                if (self.results):
                    self._set_units()
                return True
        except Exception as e:
                self.logger.info("Exception reading saved results %s, %s" % (projfile, e))
                return False

    def write_data(self, projfile):
        try:
            self.logger.info("Writing HDF 5 data to %s" % projfile)
            writer = HDF5Writer(projfile)
            self.serialize(writer)
            try:
                self.logger.info("Wrote A=%s" % self.A)
            except AttributeError:
                pass
            writer.close()
        except Exception as e:
            self.logger.exception("Exception with HDF writer for file %s" % e)

        if(not self._write_network_data(projfile)):
            return False
        if(not self._write_assetgroup_data(projfile)):
            return False
        return True

    def _write_assetgroup_data(self, projfile):
        f = self.get_assetgroups_file(projfile)

        try:
            with open(f, 'wb+') as stream:
                self.logger.info("Writing results to %s" % f)
                pickle.dump(self.group_list_to_save_or_load, stream)
                return True
        except Exception as e:
                self.logger.info("Exception writing: %s,  %s" % (f, e))
                return False

    def _write_network_data(self, projfile):
        f = self.get_nwstore_file(projfile)

        try:
            with open(f, 'wb+') as stream:
                self.logger.info("Writing results to %s" % f)
                pickle.dump(self.results, stream)
                return True
        except Exception as e:
                self.logger.info("Exception writing: %s,  %s" % (f, e))
                return False

    def get_epanetfile(self):
        try:
            return os.path.join(os.path.dirname(self.projectname), self.fname)
        except:
            return None

    def set_network(self, results):
        if (isinstance(results, ResultSet)):
            self.results = results
            self._set_units()
            return
        else:
            self.logger.warn("There was a problem with calculations ")
            if (isinstance(results, Exception)):
                self.logger.warn("Exception: %s " % results)
            else:
                self.logger.warn("Unknown object of %s" % type(results))
            self.results = None
            return

    def get_network(self):
        return self.results


def main():
    _app = QApplication([])
    if(not _app):
        raise
    # e = read_data()
    # save=e.edit()
    mw = rrpam_wds.gui.dialogs.MainWindow()
    pg = ProjectGUI(mw)
    ret = pg.open_project()
    logger = logging.getLogger()
    logger.info("Returned: %s" % str(ret))
    # if(save):
    #    write_data(e)

if __name__ == '__main__':
    main()
