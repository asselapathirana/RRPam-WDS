from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import sys
import time
import unittest
from unittest.mock import MagicMock

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


class test_main_window(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Signalling tests")

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

    def test_every_plot_triggers_selection_update_function_in_the_main_window(self):
        rm = self.aw.riskmatrix
        nm = self.aw.networkmap
        ot = list(self.aw.optimaltimegraphs.values())[0]
        rm.plot_item(5000, 50)
        with mock.patch.object(self.aw, 'update_all_plots_with_selection', autospec=True) as mock_update_all_plots_with_selection:
            self.assertFalse(mock_update_all_plots_with_selection.called)
            risk_item = [x for x in rm.get_plot().get_items() if isinstance(x, EllipseShape)][0]
            rm.get_plot().select_item(risk_item)
            self.assertTrue(mock_update_all_plots_with_selection.called)
            link = MagicMock()
            link.start.x = 50
            link.start.y = 100
            link.end.x = 500
            link.end.y = 500
            link.vertices = []
            link.id = "Foo"
            nm.draw_links([link])
            mock_update_all_plots_with_selection.reset_mock()
            self.assertFalse(mock_update_all_plots_with_selection.called)
            link_item = [x for x in nm.get_plot().get_items() if isinstance(x, CurveItem)][0]
            rm.get_plot().select_item(link_item)
            self.assertTrue(mock_update_all_plots_with_selection.called)

            mock_update_all_plots_with_selection.reset_mock()
            self.assertFalse(mock_update_all_plots_with_selection.called)
            ot.plotCurveSet("Fox", np.array([1997, 1998, 1999]), np.array(
                [8, 10, 15]), np.array([25, 20, 18]))
            ot_item = [x for x in ot.get_plot().get_items() if isinstance(x, CurveItem)][0]
            rm.get_plot().select_item(ot_item)
            self.assertTrue(mock_update_all_plots_with_selection.called)


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_main_window()
        ot.setUp()
        ot.test_every_plot_triggers_selection_update_function_in_the_main_window()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
