import os
import sys
import time
import unittest

import numpy as np
from guiqwt import tests
from guiqwt.plot import CurveDialog
from numpy.testing import assert_array_almost_equal
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.gui.dialogs import optimalTimeGraph, CurveDialogWithClosable


class test_optimal_time_graph(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing optimal time graph")

        pass

    def tearDown(self):
        global stop
        stop = time.time()
        print("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw=None
        pass

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""
        pass
    
    def test_optimalTimeGraph_is_derived_from_CurveDialogWithClosable(self):
        """optimalTimeGraph should be derived from CurveDialogWithClosable class"""
        tg1 = optimalTimeGraph("set1", None, None, None, parent=self.aw)
        self.assertIsInstance(tg1,CurveDialogWithClosable)
        self.aw.addSubWindow(tg1)


    def test_optimalTimeGraph_creates_right_three_curves(self):
        from guiqwt.curve import CurveItem
        year = np.arange(0, 50, 1)
        damagecost = year**2.1
        renewalcost = (100 - year)**1.9
        tg1 = optimalTimeGraph("set1", year, damagecost, renewalcost, parent=self.aw)
        self.aw.addSubWindow(tg1)
        it = [x for x in tg1.get_plot().get_items() if (isinstance(x, CurveItem))]
        self.assertEqual(len(it), 3)
        assert_array_almost_equal(it[0].get_data(), (year, damagecost))
        assert_array_almost_equal(it[1].get_data(), (year, renewalcost))
        assert_array_almost_equal(it[2].get_data(), (year, (damagecost + renewalcost)))
        tg1.plotCurveSet("set2", year, damagecost + 2000, renewalcost * 1.2)
        it = [x for x in tg1.get_plot().get_items() if (isinstance(x, CurveItem))]
        self.assertEqual(len(it), 6)
        assert_array_almost_equal(it[3].get_data(), (year, damagecost + 2000))
        assert_array_almost_equal(it[4].get_data(), (year, renewalcost * 1.2))
        assert_array_almost_equal(it[5].get_data(), (year, (damagecost + 2000 + renewalcost * 1.2)))
        pass


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_optimal_time_graph()
        ot.setUp()
        ot.test_optimalTimeGraph_is_derived_from_CurveDialogWithClosable()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
