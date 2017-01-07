import logging
import sys
import time
import unittest

import mock
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow


def set_text_textbox(item, value="", enter=False):
    item.clear()
    QTest.keyClicks(item, str(value))
    if (enter):
        QTest.keyPress(item, Qt.Key_Return)


def set_text_spinbox(item, value=""):  # useful for qtests.

    for i in range(3):
        QTest.keyPress(item, Qt.Key_Backspace)
        QTest.keyPress(item, Qt.Key_Delete)
    QTest.keyClicks(item, str(value))
    QTest.keyPress(item, Qt.Key_Return)


class Test_Parent(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.start = time.time()
        self.aw = MainWindow()
        self.aw.progressbar = mock.MagicMock()
        # we set progress bar to a mock. Otherwise it will
        # interfere with tests.

    def tearDown(self):
        self.stop = time.time()
        logger = logging.getLogger()
        logger.info("\ncalculation took %0.2f seconds." % (self.stop - self.start))
        self.app.processEvents()
        time.sleep(1)
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
