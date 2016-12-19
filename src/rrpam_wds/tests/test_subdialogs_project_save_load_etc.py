from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import shutil
import sys
import time
import unittest

import mock
from PyQt5.QtWidgets import QApplication

import rrpam_wds.constants as c
import rrpam_wds.gui.subdialogs as sub
from rrpam_wds.examples import networks
from rrpam_wds.gui.dialogs import MainWindow


class TestProjects(unittest.TestCase):
    start = 0
    stop = 0

    def delifexists(self, path, create=False):
        if (os.path.exists(path)):
            shutil.rmtree(path)
        if (create):
            os.mkdir(path)

    def setUp(self):
        global start
        import tempfile

        self.app = QApplication.instance() or QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("RRPAMWDS Project save open etc. tests")
        # patch standard file paths so that these tests would not pollute standard directories.
        c.HOMEDIR = tempfile.gettempdir() + "/rrpamwds_testing"
        # clean it and create it
        self.delifexists(c.HOMEDIR, create=True)

        # monkey-patch show method in rrpam_wds.gui.subdialogs.ProjectProperties
        def custom_show(self):
            self.logger.info("Show is being faked by empty method.. that just returns True")
            self.fname = os.path.join(c.HOMEDIR, "foo1.inp")
            with open(self.fname, "w+"):
                pass
            self.A = 5.0
            self.N = 1.2
            self.DRate = .2
            return (True)

        sub.ProjectPropertiesDataset.show = custom_show
        # done moneky patching

    def tearDown(self):
        global stop
        stop = time.time()
        logger = logging.getLogger()
        logger.info("calculation took %0.2f seconds." % (stop - start))
        self.app.quit()
        self.aw = None
        # clean all
        self.delifexists(c.HOMEDIR)
        self.delifexists(c.USERDATA)

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_new_project_will_create_project_name_and_data_directory(self):

        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(c.HOMEDIR, "fo")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[0], '*.inp')

                self.assertFalse(os.path.isdir(sf))
                self.aw.projectgui.new_project()
                self.assertTrue(os.path.isfile(sf + c.PROJECTEXTENSION))
                self.assertTrue(os.path.isdir(sf + c.PROJECTDATADIREXT))
                self.assertTrue(os.path.isfile(
                    os.path.join(os.path.dirname(sf), networks[0])
                ))
                self.assertEqual(self.aw.LASTPROJECT, sf + c.PROJECTEXTENSION)

                # start fresh
                self.close_and_recreate()

        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(c.HOMEDIR, "fo")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[0], '*.inp')

                # Also try with extension
                sf = os.path.join(c.HOMEDIR, "fo" + c.PROJECTEXTENSION)
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                self.assertFalse(os.path.isdir(sf))
                self.aw.projectgui.new_project()
                self.assertTrue(os.path.isfile(sf))
                self.assertTrue(os.path.isdir(sf[:-len(c.PROJECTEXTENSION)] + c.PROJECTDATADIREXT))
                self.assertTrue(os.path.isfile(
                    os.path.join(os.path.dirname(sf), networks[0])
                ))
                self.assertEqual(self.aw.LASTPROJECT, sf)

    def close_and_recreate(self):
        self.aw.close()
        # now start a new session.
        self.app.closeAllWindows()
        self.app.exit()
        self.app = None
        time.sleep(1)
        self.app = QApplication([])
        self.aw = MainWindow()

    def test_save_project_will_save_the_project_data_to_the_project_file_and_open_project_will_read_it(
            self):
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(c.HOMEDIR, "fo")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                nw = networks[0]
                mock__getSaveFileName2.return_value = (nw, '*.inp')

                self.assertFalse(os.path.isdir(sf))
                self.aw.projectgui.new_project()
                oldA = self.aw.projectgui.projectproperties.dataset.A = 25.0
                self.aw.projectgui.save_project()
                self.assertTrue(os.path.isfile(sf + c.PROJECTEXTENSION))
                self.assertTrue(os.path.isdir(sf + c.PROJECTDATADIREXT))
                # start fresh
                self.close_and_recreate()

                self.assertEqual(self.aw.LASTPROJECT, sf + c.PROJECTEXTENSION)

        oldvals = {"A": oldA, "fname": os.path.basename(nw)}
        self.open_and_check(sf, oldvals)
        return sf, oldvals

    def open_and_check(self, sf, oldvals):
        # cleanly open a new case
        self.close_and_recreate()
        # invalidate show() method - (we have patched it, if the code below
        # somehow calls it, our test is meaningless!)
        sub.ProjectPropertiesDataset.show = None
        # If show is called now, it will create an exception
        with self.assertRaises(TypeError):
            sub.ProjectPropertiesDataset.show()

        with mock.patch.object(self.aw.projectgui, '_getOpenFileName', autospec=True) as mock__getOpenFileName:
            mock__getOpenFileName.return_value = (sf + c.PROJECTEXTENSION, c.PROJECTEXTENSION)
            self.aw.projectgui.open_project()
            self.assertEqual(oldvals['A'], self.aw.projectgui.projectproperties.dataset.A)
            self.assertEqual(oldvals['fname'], self.aw.projectgui.projectproperties.dataset.fname)

    def test_save_project_as_with_filename_with_extention_or_without_will_create_project_file_and_directory(
            self):
        # first create a project and open it
        sf, oldvals = self.test_save_project_will_save_the_project_data_to_the_project_file_and_open_project_will_read_it(
        )
        # now save it as
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            sfnew = os.path.join(c.HOMEDIR, "new_fo")
            mock__getSaveFileName.return_value = (sfnew, c.PROJECTEXTENSION)
            self.assertFalse(os.path.isdir(sfnew))
            self.aw.projectgui.save_project_as()

        self.open_and_check(sfnew, oldvals)


def clt(tc, fn, mainwindow=None):
    if(not mainwindow):
        tc.setUp()
    else:
        tc.aw = mainwindow
    fn()
    tc.aw.projectgui
    tc.aw.show()
    tc.app.exec_()
    if(not mainwindow):
        tc.tearDown()


def main(test=True, mainwindow=None):
    if(test):
        unittest.main(verbosity=2)
    else:
        tc = TestProjects()
        for a in dir(tc):
            if (a.startswith(
                    'test_save_project_as_with_filename_with_extention_or_without_will_create_project_file_and_directory')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    print("************** calling %s **********************************" % a)
                    clt(tc, b, mainwindow)

if __name__ == "__main__":
    main(test=False)
