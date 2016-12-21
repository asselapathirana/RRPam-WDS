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
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox

import rrpam_wds.constants as c
import rrpam_wds.gui.dialogs
from rrpam_wds.constants import ResultSet


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
            self.logger.info("A=%s, N=%s" % (k.A, k.N))
        except Exception:
            pass

    def rewrite_values_in_gui_with_variables(self):
        self.logger.info("Writing: var>GUI ")
        self.log()
        self.projectproperties.get()

    def rewrite_values_in_variables_with_gui(self):
        self.logger.info("Writing: GUI>var ")
        self.log()
        self.projectproperties.set()

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

    def _save_project_to_dest(self, projectfile, epanetfile=None):

        prjname, subdir, ext = self._get_dir_and_extention(projectfile)
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

    def _get_dir_and_extention(self, projectname):
        self.logger.info("Analysing prjname : %s", projectname)
        if(projectname[-4:] != c.PROJECTEXTENSION):
            t = projectname + c.PROJECTEXTENSION
        else:
            t = projectname
        prjname, subdir, ext = (t, t[:-4] + c.PROJECTDATADIREXT, t[-4:])
        self.logger.info("Returning prjname:%s, subdir:%s and ext:%s" % (prjname, subdir, ext))

        return prjname, subdir, ext

    def save_project(self):
        self.logger.info("Saving the project")
        # Implement the actions needed to save the project here.
        # first update any user changes in parameters
        self.rewrite_values_in_variables_with_gui()
        self._save_project_to_dest(self.projectproperties.dataset.projectname)

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
            projectfile, dir, ext = self._get_dir_and_extention(projectfile)
            self.logger.info("Selected file to open : %s " % projectfile)
            # check if it is a valid project
            if(self._valid_project(projectfile)):
                self.projectproperties.dataset.projectname = projectfile
                self.parent.LASTPROJECT = self.projectproperties.dataset.projectname
                self.parent._display_project()
                break
            else:
                self.logger.info("Project loading failed: Not a valid project")
                return None

        self.logger.info("Open Project valid")
        self.rewrite_values_in_gui_with_variables()
        return (projectfile)

    def _valid_project(self, prj):
        """Check if prj represents a valid project. """
        if (not os.path.isfile(prj)):
            return False
        if (not os.path.isdir(self._get_dir_and_extention(prj)[1])):
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
    _eg4 = dt.EndGroup("Project Location")
    _bg3 = dt.BeginGroup("Epanet file of this project")
    fname = di.StringItem("", help="Epanet file of this project").set_prop("display", active=False)
    _eg3 = dt.EndGroup("Epanet file of this project")
    di.FileOpenItem("Select Epanet file (open)", ("inp", "eta"))
    _bg2 = dt.BeginGroup("Discount rate (%)")
    DRate = di.FloatItem("", default=10, min=-5, max=+50, step=0.1, slider=True)
    _eg2 = dt.EndGroup("Discount rate (%)")
    _bg = dt.BeginGroup("Aging rate")
    A = di.FloatItem(" A", default=1, min=None, max=None,
                     nonzero=True, unit='',
                     slider=False,
                     help='', check=True)
    N = di.FloatItem("N0", default=2)
    _eg = dt.EndGroup("Aging rate")

    def __init__(self, title=None, comment=None, icon=''):
        self.logger = logging.getLogger()
        self.results = None
        super(ProjectPropertiesDataset, self).__init__(title, comment, icon)

    # def show(self):
    #    return self.edit()
    def get_nwstore_file(self, f):
        return f + "__"

    def read_data(self, projfile):
        if os.path.exists(projfile):
            try:
                self.logger.info("Reading HDF 5 data from %s" % projfile)
                reader = HDF5Reader(projfile)
                self.deserialize(reader)
                try:
                    self.logger.info("Read A=%s" % self.A)
                except AttributeError:
                    pass
                reader.close

            except:
                self.logger.info("Exception with HDF reader for file %s" % projfile)
                return False

            f = self.get_nwstore_file(projfile)

            try:
                with open(f, 'rb') as stream:
                    self.logger.info("Reading results  from %s" % f)
                    self.results = pickle.load(stream)
                    return True
            except Exception as e:
                    self.logger.info("Exception reading saved results %s, %s" % (projfile, e))
                    return False
        else:
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

        f = self.get_nwstore_file(projfile)

        try:
            # if (not self.results):
            #    return
            with open(f, 'wb+') as stream:
                self.logger.info("Writing results to %s" % f)
                pickle.dump(self.results, stream)
        except Exception as e:
                self.logger.info("Exception writing: %s,  %s" % (f, e))

    def get_epanetfile(self):
        try:
            return os.path.join(os.path.dirname(self.projectname), self.fname)
        except:
            return None

    def set_network(self, results):
        if (isinstance(results, ResultSet)):
            self.results = results
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
