from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import sys
import time
import unittest

from guiqwt.shapes import EllipseShape
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.gui.dialogs import RiskMatrix
from guiqwt.label import LabelItem


class test_risk_matrix(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing risk matrix")

    def tearDown(self):
        global stop
        stop = time.time()
        print("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_Risk_Map_is_derived_from_CurveDialogWithClosable(self):
        self.rm = RiskMatrix(mainwindow=self.aw)
        self.aw.addSubWindow(self.rm)
        self.rm.show()
        isinstance(self.rm, CurveDialogWithClosable)

    def test_plot_item_will_create_a_circle(self):
        self.rm = RiskMatrix(mainwindow=self.aw)
        self.aw.addSubWindow(self.rm)
        self.rm.show()
        pts0 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.draw_some_circles()
        pts1 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.assertEqual(len(pts1), len(pts0) + 4)
        self.assertEqual(pts1[1].get_xdiameter(), self.rm.get_ellipse_xaxis(1000., 20.))

    def test_plot_item_will_create_two_entitites_circle_and_label_each_with_id_(self):
        self.rm = RiskMatrix(mainwindow=self.aw)
        self.aw.addSubWindow(self.rm)
        self.rm.show()
        pts0 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.draw_some_circles()
        pts1 = [x.id_ for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        labs = [x.id_ for x in self.rm.get_plot().get_items() if isinstance(x, LabelItem)]
        self.assertEqual(pts1.sort(), labs.sort())
        self.assertEqual(len(pts1), len(pts0) + 4)

    def draw_some_circles(self):
        self.rm.plot_item("foo", [5000.0, 50], title="foo")
        self.rm.plot_item("bar", [1000.0, 20], title="bar")
        self.rm.plot_item("bax", [8000.0, 70], title="bax")
        self.rm.plot_item("bax", [15000.0, 100], title="bax")


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_risk_matrix()
        ot.setUp()
        ot.test_plot_item_will_create_a_circle()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
