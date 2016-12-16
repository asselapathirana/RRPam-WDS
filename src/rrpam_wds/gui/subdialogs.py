from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA

import logging
import os

import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt
from guidata.hdf5io import HDF5Reader
from guidata.hdf5io import HDF5Writer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog

import rrpam_wds.constants as c
import rrpam_wds.gui.dialogs


class ProjectGUI():
    logger = logging.getLogger()
    LASTPROJECT = None

    def __init__(self, parent):
        self.parent = parent
        self._load_history()

    def _load_history(self):
        """If there is an existing configuration load it."""
        if(os.path.isfile(c.PROJECTDATA)):
            with open(c.PROJECTDATA, "r") as f:
                self.LASTPROJECT = f.read()

    def _save_history(self, projectfile):
        self.logger.info("Testing projectfilename %s as save candidate" % projectfile)
        if(self._get_dir_and_extention(projectfile)[-1] == c.PROJECTEXTENSION):
            self.LASTPROJECT = projectfile
        else:
            self.LASTPROJECT = projectfile + c.PROJECTEXTENSION
        self.logger.info("Saving  %s into history file" % self.LASTPROJECT)

        try:
            with open(c.PROJECTDATA, "w+") as f:
                f.write(self.LASTPROJECT)
        except:
            pass

    def new_project(self):
        self.logger.info("New Project")
        msg = "New Project"
        self._create_empty_project(msg, new=True)

    def _getSaveFileName(self, *args, **kwargs):
        self.logger.info("proxy calling QFileDialog.getSaveFileName ")
        return QFileDialog.getSaveFileName(*args, **kwargs)

    def _getOpenFileName(self, *args, **kwargs):
        self.logger.info("proxy calling QFileDialog.getOpenFileName ")
        return QFileDialog.getOpenFileName(*args, **kwargs)

    def _create_empty_project(self, msg, new=False):
        prj = self.LASTPROJECT

        self.try_loading_project_properties(prj)

        projectfile, filter = self._getSaveFileName(self.parent,
                                                    msg,
                                                    self.LASTPROJECT or c.HOMEDIR,
                                                    filter='*' + c.PROJECTEXTENSION)
        self.logger.info("Selected file for new project : %s " % projectfile)
        if(not projectfile):
            return False
        if ((not hasattr(self, "projectproperties")) or (not self.projectproperties)):
            self.projectproperties = ProjectProperties(self._get_dir_and_extention(projectfile)[0])
        if(new):
            if (not self.projectproperties.show()):
                self.logger.info("User cancelled the project properties dialog. ")
                return False

        self.projectproperties.write_data()
        projectfile, subdirn, ext = self._get_dir_and_extention(projectfile)
        self._save_history(projectfile)

        if(not os.path.isdir(subdirn)):
            os.mkdir(subdirn)
        return True

    def try_loading_project_properties(self, prj):

        self.projectproperties = ProjectProperties(prj)
        try:
            self.logger.info("Trying to read data from last recorded project ..")
            if(self.projectproperties.read_data()):
                self.logger.info("... Last project read successfully.")
                return True
            else:
                self.projectproperties = None
                return False
        except:
            self.projectproperties = None
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

    def save_project_as(self):
        msg = "Save project as"
        self._create_empty_project(msg)
        self.save_project()

    def open_project(self):
        while (True):
            projectfile, filter = self._getOpenFileName(self.parent,
                                                        "Open project",
                                                        self.LASTPROJECT or c.USERDATA,
                                                        filter='*' + c.PROJECTEXTENSION)
            if(not projectfile):
                return None
            self.logger.info("Selected file to open : %s " % projectfile)
            # check if it is a valid project
            if(self._valid_project(projectfile)):
                self._save_history(projectfile)
                break

        self.logger.info("Open Project valid")
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


class ProjectProperties(dt.DataSet):

    """Project : """

    fname = di.FileOpenItem("Select Epanet file (open)", ("inp", "eta"))
    DRate = di.FloatItem("Discount rate (%)", default=10, min=-5, max=+50, step=0.1, slider=True)
    _bg = dt.BeginGroup("Aging rate")
    A = di.FloatItem(" A", default=1, min=None, max=None,
                     nonzero=True, unit='',
                     slider=False,
                     help='', check=True)
    N = di.FloatItem("N0", default=2)
    _eg = dt.EndGroup("Aging rate")

    def __init__(self, projectfilename, title=None, comment=None, icon=''):
        self.logger = logging.getLogger()
        self.projectfilename = projectfilename
        super(ProjectProperties, self).__init__(title, comment, icon)

    def show(self):
        return self.edit()

    def read_data(self):
        self.logger.info("Reading HDF 5 data from %s" % self.projectfilename)
        if os.path.exists(self.projectfilename):
            try:
                reader = HDF5Reader(self.projectfilename)
                self.deserialize(reader)
                reader.close()
                return True
            except:
                self.logger.info("Exception with HDF reader for file %s" % self.projectfilename)

        return False

    def write_data(self):
        self.logger.info("Writing HDF 5 data to %s" % self.projectfilename)
        try:
            writer = HDF5Writer(self.projectfilename)
            self.serialize(writer)
            writer.close()
        except:
            self.logger.info("Exceptino with HDF writer for file %s" % self.projectfilename)


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
