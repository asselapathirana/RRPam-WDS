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
        self.projectproperties=None


    def new_project(self):
        self.logger.info("New Project")
        msg = "New Project"
        tmp=self._create_empty_project(msg, new=True)
        if(tmp):
            self.projectfile=tmp

    def _getSaveFileName(self, *args, **kwargs):
        self.logger.info("proxy calling QFileDialog.getSaveFileName ")
        return QFileDialog.getSaveFileName(*args, **kwargs)

    def _getOpenFileName(self, *args, **kwargs):
        self.logger.info("proxy calling QFileDialog.getOpenFileName ")
        return QFileDialog.getOpenFileName(*args, **kwargs)

    def _create_empty_project(self, msg, new=False):

        projectfile = self.get_save_filename(msg)
        if(not projectfile):
            return None        
        else:
            return self._save_project_to_dest(projectfile)

    def get_save_filename(self, msg):
        projectfile, filter = self._getSaveFileName(self.parent,
                                                    msg,
                                                    self.parent.LASTPROJECT or c.HOMEDIR,
                                                    filter='*' + c.PROJECTEXTENSION)
        self.logger.info("Selected file for save/new project : %s " % projectfile)
        return projectfile

    def _save_project_to_dest(self, projectfile):

        prjname, subdir, ext= self._get_dir_and_extention(projectfile)
        if(not self.projectproperties):
            self.projectproperties = ProjectProperties(self)
        self.projectproperties.write_data(prjname)
        if(not os.path.isdir(subdir)):
            os.mkdir(subdir)
        return prjname

    def try_loading_project_properties(self, prj):

        tmp = ProjectProperties(self)
        try:
            self.logger.info("Trying to read properties from %s " % prj)
            if(tmp.read_data(prj)):
                self.logger.info(" %s project read successfully." % prj)
                self.projectproperties=tmp
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
        self._save_project_to_dest(self.projectfile)

    def save_project_as(self, target):
        msg = "Save project as"
        self.projectfile=self.get_save_filename(msg)
        self.save_project()

    def open_project(self):
        while (True):
            projectfile, filter = self._getOpenFileName(self.parent,
                                                        "Open project",
                                                        self.parent.LASTPROJECT or c.HOMEDIR,
                                                        filter='*' + c.PROJECTEXTENSION)
            if(not projectfile):
                return None
            self.logger.info("Selected file to open : %s " % projectfile)
            # check if it is a valid project
            if(self._valid_project(projectfile)):
                self.projectfile=projectfile
                break
            else:
                self.logger.info("Project loading failed: Not a valid project")
                return None

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

    def __init__(self,  title=None, comment=None, icon=''):
        self.logger = logging.getLogger()
        super(ProjectProperties, self).__init__(title, comment, icon)

    def show(self):
        return self.edit()

    def read_data(self, projfile):
        self.logger.info("Reading HDF 5 data from %s" % projfile)
        if os.path.exists(projfile):
            try:
                reader = HDF5Reader(projfile)
                self.deserialize(reader)
                reader.close()
                return True
            except:
                self.logger.info("Exception with HDF reader for file %s" % projfile)

        return False

    def write_data(self, projfile):
        self.logger.info("Writing HDF 5 data to %s" % projfile)
        try:
            writer = HDF5Writer(projfile)
            self.serialize(writer)
            writer.close()
        except Exception as e:
            self.logger.exception("Exceptino with HDF writer for file %s" % e)


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
