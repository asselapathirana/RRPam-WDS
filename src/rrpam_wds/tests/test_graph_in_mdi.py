from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import sys
import time
import unittest

from guiqwt.plot import CurveDialog
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow


class mdi_graph_test(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication.instance() or QApplication(sys.argv)

        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing multi document window")

    def tearDown(self):
        global stop
        stop = time.time()
        logger = logging.getLogger()
        logger.info("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None

    def test_graph_window_properly_added_to_MDI(self):
        self.graph = CurveDialog(
            wintitle="XXX YYH #DKLJLKFE Kadk #kdfd", icon="guiqwt.svg",
            edit=False,
            toolbar=True,
            options=None,
            parent=self.aw,
            panels=None)

        self.aw.addSubWindow(self.graph)
        self.assertEqual(self.aw.mdi.subWindowList()[
                         -1].windowTitle(), self.graph.windowTitle())

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_dummy(self):
        pass


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = mdi_graph_test()
        ot.setUp()
        ot.test_graph_window_properly_added_to_MDI()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
