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
from PyQt5 import QtCore 

from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.project_manager import ProjectManager as PM


def trigger_sub_menu_item(mainwindow, menutext, submenutext):
    filemenu = [x for x in mainwindow.menuBar().actions() if x.text() == menutext][0]
    sb = filemenu.menu()
    sm = [x for x in sb.actions() if x.text() == submenutext][0]
    sm.trigger()  # don't use toggle, use trigger.


class TestGeometry(unittest.TestCase):
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
        
    def test_main_window_remember_geometry(self):
        oldgeometry=QtCore.QRect(10, 10, 1000, 750)
        self.aw.setGeometry(oldgeometry)
        self.aw.close()
        # now start a new session.
        self.app.closeAllWindows()
        self.app.exit()
        self.app=None
        time.sleep(1)
        self.app=QApplication([])
        self.aw=MainWindow()
        self.assertEqual(self.aw.geometry(),oldgeometry)
        
        
        
def clt(tc, fn, mainwindow=None):
    if(not mainwindow):
        tc.setUp()
    else:
        tc.aw = mainwindow
    fn()
    tc.aw.show()
    tc.app.exec_()    
    
    if(not mainwindow):
        tc.tearDown()


def main(test=True, mainwindow=None):
    if(test):
        unittest.main(verbosity=2)
    else:
        tc = TestGeometry()
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