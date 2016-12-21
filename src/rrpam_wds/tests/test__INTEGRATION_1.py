from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import sys
import time
import unittest

import mock
from PyQt5.QtWidgets import QApplication

from rrpam_wds import constants as c
from rrpam_wds.examples import networks
from rrpam_wds.gui.dialogs import MainWindow


def trigger_sub_menu_item(mainwindow, menutext, submenutext):
    filemenu = [x for x in mainwindow.menuBar().actions() if x.text() == menutext][0]
    sb = filemenu.menu()
    sm = [x for x in sb.actions() if x.text() == submenutext][0]
    sm.trigger()  # don't use toggle, use trigger.


class TestProjects(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication.instance() or QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.logger = logging.getLogger()
        self.aw.setWindowTitle("RRPAMWDS Projject tests")
        self.logger.info("Finished setup for the test. ")

    def tearDown(self):
        global stop
        stop = time.time()
        self.aw.pm.wait_to_finish()
        logger = logging.getLogger()
        logger.info("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_clicking_file_new_and_wait_for_network_to_be_displayed(self):
        """This is the test for opening and existing project. For the moment, the project details are hard-coded.
        As we implement real project opening, this test will have to change. """
        import tempfile
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(tempfile.tempdir, "xxx3xp")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[0], '*.inp')
                time.sleep(.1)
                self.app.processEvents()
                idthings = [x for x in self.aw.networkmap.get_plot().get_items()
                            if hasattr(x, "id_")]
                self.assertEqual(0, len(idthings))
                # now we can non-interactively test new_project.
                trigger_sub_menu_item(
                    self.aw,
                    self.aw.menuitems.file,
                    self.aw.menuitems.new_project)
                time.sleep(.1)
                self.app.processEvents()
                # make sure the thread finishes
                self.aw.pm.wait_to_finish()
                # but give some time for gui to plot too.
                self.app.processEvents()
                time.sleep(1)
                idthings = [x for x in self.aw.networkmap.get_plot().get_items()
                            if hasattr(x, "id_")]
                self.assertGreater(len(idthings), 5)


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
        tc = TestProjects()
        for a in dir(tc):
            if (a.startswith(
                    'test_')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    print("Calling %s" % a)
                    logger = logging.getLogger()
                    logger.info("calling %s **********************************" % a)
                    clt(tc, b, mainwindow)
                    print("Called %s" % a)


if __name__ == "__main__":
    main(test=False)
