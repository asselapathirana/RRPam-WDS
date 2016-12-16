from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import random
import sys
import time
import unittest

import mock
from guiqwt.curve import CurveItem
from guiqwt.shapes import EllipseShape
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.project_manager import ProjectManager as PM
from rrpam_wds.tests.test_rrpamwds_projects  import trigger_sub_menu_item

class TestProjects(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("RRPAMWDS Projject tests")

    def tearDown(self):
        global stop
        stop = time.time()
        logger = logging.getLogger()
        logger.info("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""
        
        
    def test_clicking_new_project_will_call_new_project_method_in_subdialogs_project_class(self):
        
        
        
        
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
                    'test_clicking_window_log_window_will_call_show_logwindow_method')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    print("Calling %s" % a)
                    logger = logging.getLogger()
                    logger.info("calling %s **********************************" % a)
                    clt(tc, b, mainwindow)
                    print("Called %s" % a)


if __name__ == "__main__":
    main(test=False)
