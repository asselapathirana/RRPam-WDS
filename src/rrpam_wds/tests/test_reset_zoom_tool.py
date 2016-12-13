from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import sys
import time
import unittest

from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.custom_toolbar_items import ResetZoomTool
from rrpam_wds.gui.dialogs import MainWindow


class test_reset_zoom_tool(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing optimal time graph")

    def tearDown(self):
        global stop
        stop = time.time()
        print("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_toolbar_has_reset_zoom_tool(self):
        self.win = self.aw.new_window(mainwindow=self.aw)
        tb = self.win.get_default_toolbar()
        self.assertTrue([x for x in tb.actions() if x.text() == ResetZoomTool.TITLE])


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_reset_zoom_tool()
        ot.setUp()
        ot.test_toolbar_has_reset_zoom_tool()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
