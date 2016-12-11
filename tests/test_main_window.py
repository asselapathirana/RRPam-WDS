from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import sys
import time
import unittest

import numpy as np
import pytest
from guiqwt import tests
from guiqwt.plot import CurveDialog
from numpy.testing import assert_array_almost_equal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea

from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.gui.dialogs import NetworkMap
from rrpam_wds.gui.dialogs import RiskMatrix
from rrpam_wds.gui.dialogs import optimalTimeGraph


class test_main_window(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing main window")

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

    def test_mainwindow_is_derived_from_QMainWindow(self):
        """optimalTimeGraph should be derived from CurveDialogWithClosable class"""
        self.assertIsInstance(self.aw, QMainWindow)

    def test_mainwindow_has_a_mdi_Area(self):
        self.assertIsInstance(self.aw.mdi, QMdiArea)

    def test_mainwindow_always_has_a_network_map_and_risk_matrix_one_each(self):
        list1 = self.aw.mdi.subWindowList()
        self.assertTrue(len([x for x in list1 if (isinstance(x.widget(), RiskMatrix))]), 1)
        self.assertTrue(len([x for x in list1 if (isinstance(x.widget(), NetworkMap))]), 1)

    def test_main_window_will_not_add_more_than_one_network_map_or_risk_matrix(self):
        self.aw.standard_windows()  # Adds riskmatrix, network map and a optimaltimegraph
        list1 = self.aw.mdi.subWindowList()  # should have above three
        self.aw.add_riskmatrix()  # try adding a rm
        self.aw.add_networkmap()  # try adding a nm
        self.aw.standard_windows()  # this will add only an extra optimaltimegraph
        list2 = self.aw.mdi.subWindowList()
        list1 = [x for x in list1 if not isinstance(x.widget(), optimalTimeGraph)]
        list2 = [x for x in list2 if not isinstance(x.widget(), optimalTimeGraph)]
        self.assertEqual(list1, list2)

    def test_attempting_to_close_will_minimize_network_map_and_risk_matrix_and_the_last_optimal_time_graph(
            self):

        list1 = self.aw.mdi.subWindowList()
        self.assertFalse(self.aw.riskmatrix.isMinimized())
        self.assertFalse(self.aw.networkmap.isMinimized())
        self.close_all_windows()
        list2 = self.aw.mdi.subWindowList()
        self.assertEqual(list1, list2)
        self.assertTrue(self.aw.networkmap.isMinimized())
        self.assertTrue(self.aw.networkmap.isMinimized())

    def close_all_windows(self):
        for w in self.aw.mdi.subWindowList():
            w.close()

    def test_multiple_optimal_time_graphs_can_be_added(self):
        list1 = self.aw.mdi.subWindowList()
        self.assertTrue(len([x for x in list1 if (isinstance(x.widget(), optimalTimeGraph))]), 1)
        self.aw.add_optimaltimegraph()
        self.assertEqual(len(list1) + 1, len(self.aw.mdi.subWindowList()))

    def test_last_remaining_optimal_time_graph_will_not_be_deleted_but_minimized(self):
        list1 = self.aw.mdi.subWindowList()
        self.aw.add_optimaltimegraph()  # now we have two
        self.aw.add_optimaltimegraph()  # now we have
        self.close_all_windows()
        list2 = self.aw.mdi.subWindowList()
       # print(list1)
       # print(list2)
        self.assertEqual(len(list1), len(list2))

        for w in self.aw.mdi.subWindowList():
            self.assertTrue(w.isMinimized())


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_main_window()
        ot.setUp()
        ot.test_last_remaining_optimal_time_graph_will_not_be_deleted_but_minimized()
        # ot.aw.show()
        # sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)