from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import sys
import time
import unittest
import mock
import numpy as np
import pytest
from guiqwt import tests
from guiqwt.curve import CurveItem
from guiqwt.plot import CurveDialog
from guiqwt.shapes import EllipseShape
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


class test_keeping_records(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Records tests")

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

    def test_riskmatrix_report_adding_to_the_register(self):
        rm = self.aw.riskmatrix

        with mock.patch.object(rm, 'add_plot_item_to_record', autospec=True) as mock_add_plot_item_to_record:
            self.assertFalse(mock_add_plot_item_to_record.called)
            rm.plot_item("fox", [5000, 50], title="fox")
            self.assertTrue(mock_add_plot_item_to_record.called)


    def test_riskmatrix_report_removing_to_the_register(self):
        rm = self.aw.riskmatrix
        
        with mock.patch.object(rm, 'remove_plot_item_from_record', autospec=True) as mock_remove_plot_item_from_record:
            self.assertFalse(mock_remove_plot_item_from_record.called)
            rm.plot_item("fox", [5000, 50], title="fox")
            self.assertFalse(mock_remove_plot_item_from_record.called)
            risk_item = [x for x in rm.get_plot().get_items() if isinstance(x, EllipseShape)][0]
            rm.get_plot().del_item(risk_item)
            self.assertTrue(mock_remove_plot_item_from_record.called)      


    def test_networkmap_report_adding_to_the_register(self):
        otg = self.aw.networkmap
        
        with mock.patch.object(otg, 'add_plot_item_to_record', autospec=True) as mock_add_plot_item_to_record:
            self.assertFalse(mock_add_plot_item_to_record.called)
            otg.plot_item("fox", [(5,10),(8,3),(24,1)], "fox")
            self.assertTrue(mock_add_plot_item_to_record.called)


    def test_networkmap_report_removing_to_the_register(self):
        otg = self.aw.networkmap
        
        with mock.patch.object(otg, 'remove_plot_item_from_record', autospec=True) as mock_remove_plot_item_from_record:
            self.assertFalse(mock_remove_plot_item_from_record.called)
            otg.plot_item("fox", [(5,10),(8,3),(24,1)], "fox")
            self.assertFalse(mock_remove_plot_item_from_record.called)
            nw_item = [x for x in otg.get_plot().get_items() if isinstance(x, CurveItem)][0]
            otg.get_plot().del_item(nw_item)
            self.assertTrue(mock_remove_plot_item_from_record.called)


    def test_optimaltimegraph_report_adding_to_the_register(self):
        otg = list(self.aw.optimaltimegraphs.values())[0]
        
        with mock.patch.object(otg, 'add_plot_item_to_record', autospec=True) as mock_add_plot_item_to_record:
            self.assertFalse(mock_add_plot_item_to_record.called)
            otg.plot_item("fox",[[1997,1998,2005,2008],[5,10,25,95],[100,50,25,12]],"fox")
            self.assertTrue(mock_add_plot_item_to_record.called)


    def test_optimaltimegraph_report_removing_to_the_register(self):
        otg = list(self.aw.optimaltimegraphs.values())[0]
        
        with mock.patch.object(otg, 'remove_plot_item_from_record', autospec=True) as mock_remove_plot_item_from_record:
            self.assertFalse(mock_remove_plot_item_from_record.called)
            otg.plot_item("fox",[[1997,1998,2005,2008],[5,10,25,95],[100,50,25,12]],"fox")
            self.assertFalse(mock_remove_plot_item_from_record.called)
            nw_item = [x for x in otg.get_plot().get_items() if isinstance(x, CurveItem)][0]
            otg.get_plot().del_item(nw_item)
            self.assertTrue(mock_remove_plot_item_from_record.called)


    def test_deleting_a_curve_in_optimaltimegraph_removes_all_three_curves(self):
        # for the heck of it add another optimal time graph
        self.aw.add_optimaltimegraph()
        l= list(self.aw.optimaltimegraphs.values())
        otg1 =l[0]
        otg2 =l[1]
        self.assertEqual(len(otg1.myplotitems),0)
        otg1.plot_item("fox",[[1997,1998,2005,2008],[5,10,25,95],[100,50,25,12]],"fox")
        otg2.plot_item("fox",[[1997,1998,2005,2008],[5,10,25,95],[100,50,25,12]],"fox")
        self.assertEqual(len(otg1.myplotitems),1)
        self.assertEqual(len(otg2.myplotitems),1)
        otg_item = [x for x in otg1.get_plot().get_items() if isinstance(x, CurveItem)][0]
        otg1.get_plot().del_item(otg_item) 
        self.assertEqual(len(otg1.myplotitems),0)
        otg_item = [x for x in otg2.get_plot().get_items() if isinstance(x, CurveItem)][2] # pick a different curve from the set!
        otg2.get_plot().del_item(otg_item) 
        self.assertEqual(len(otg2.myplotitems),0)        
        
        
        

def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_keeping_records()
        ot.setUp()
        ot.test_deleting_a_curve_in_optimaltimegraph_removes_all_three_curves()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
