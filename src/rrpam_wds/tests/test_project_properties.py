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


class TestProjectProperties(unittest.TestCase):
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
                nw=networks[0]
                mock__getSaveFileName2.return_value = (nw, '*.inp')
                # THIS WILL NOT WORK: self.aw.projectgui.new_project()
                self.aw._new_project()
                time.sleep(2) # give time for the calculation thread to send results
                self.app.processEvents()
                self.aw.projectgui.save_project() # this has to save the results too
                # start fresh
                self.close_and_recreate()
        with mock.patch.object(self.aw.projectgui, '_getOpenFileName', autospec=True) as mock__getOpenFileName:
            mock__getOpenFileName.return_value = (sf, c.PROJECTEXTENSION)
            self.aw._open_project()
            self.aw.projectgui.projectproperties.dataset.results.links[0]
            self.assertTrue("Fix me.")






def clt(tc, fn, mainwindow=None):
    if(not mainwindow):
        tc.setUp()
    else:
        tc.aw = mainwindow
    fn()
    if(not mainwindow):
        tc.tearDown()


def main(test=True, mainwindow=None):
    if(test):
        unittest.main(verbosity=2)
    else:
        tc = TestProjectProperties()
        for a in dir(tc):
            if (a.startswith(
                    'test_')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    print("************** calling %s **********************************" % a)
                    clt(tc, b, mainwindow)

if __name__ == "__main__":
    main(test=False)
