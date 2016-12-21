import logging
import sys
import time
import unittest

from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow


class Test_Parent(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.start = time.time()
        self.aw = MainWindow()

    def tearDown(self):
        self.stop = time.time()
        logger = logging.getLogger()
        logger.info("\ncalculation took %0.2f seconds." % (self.stop - self.start))
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""


def clt(tc, fn, mainwindow=None):  # pragma: no cover
    if(not mainwindow):
        tc.setUp()
    else:
        tc.aw = mainwindow
    fn()
    if(not mainwindow):
        tc.tearDown()


def main(cls, test=True, mainwindow=None):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        tc = cls()
        for a in dir(tc):
            if (a.startswith('test_')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    logger = logging.getLogger()
                    logger.info("calling %s **********************************" % a)
                    print("calling %s **********************************" % a)
                    clt(tc, b, mainwindow)
