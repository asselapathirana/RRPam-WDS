from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import sys
import time
import unittest

import numpy as np
from guiqwt import tests
from guiqwt.plot import CurveDialog
from guiqwt.shapes import EllipseShape
from numpy.testing import assert_array_almost_equal
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs
from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.gui.dialogs import RiskMatrix


class test_risk_matrix(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing risk matrix")
        self.rm = RiskMatrix()
        self.aw.addSubWindow(self.rm)
        self.rm.show()
        pass

    def tearDown(self):
        global stop
        stop = time.time()
        print("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None
        pass

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""
        pass

    def test_Risk_Map_is_derived_from_CurveDialogWithClosable(self):

        isinstance(self.rm, CurveDialogWithClosable)

    def test_plot_item_will_create_a_circle(self):
        pts0 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.rm.plot_item(5000.0, 50, title="foo")
        self.rm.plot_item(1000.0, 20, title="bar")
        self.rm.plot_item(8000.0, 70, title="bax")
        pts1 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.assertEqual(len(pts1), len(pts0) + 3)


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
