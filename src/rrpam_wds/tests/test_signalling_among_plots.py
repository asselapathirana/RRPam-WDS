from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import sys
import time
import unittest

import mock
import numpy as np
from guiqwt.curve import CurveItem
from guiqwt.shapes import EllipseShape
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow


class test_main_window(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Signalling tests")

    def tearDown(self):
        global stop
        stop = time.time()
        logger = logging.getLogger()
        logger.info("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_every_plot_triggers_selection_update_function_in_the_main_window(self):
        nm, rm, ot = self.plot_a_random_dataset()
        with mock.patch.object(self.aw, 'update_all_plots_with_selection', autospec=True) as mock_update_all_plots_with_selection:
            self.assertFalse(mock_update_all_plots_with_selection.called)
            risk_item = [x for x in rm.get_plot().get_items() if isinstance(x, EllipseShape)][0]
            rm.get_plot().select_item(risk_item)
            self.assertTrue(mock_update_all_plots_with_selection.called)
            mock_update_all_plots_with_selection.reset_mock()
            self.assertFalse(mock_update_all_plots_with_selection.called)
            link_item = [x for x in nm.get_plot().get_items() if isinstance(x, CurveItem)][0]
            nm.get_plot().select_item(link_item)
            mock_update_all_plots_with_selection.assert_called_with(nm.get_plot())

            mock_update_all_plots_with_selection.reset_mock()
            self.assertFalse(mock_update_all_plots_with_selection.called)
            ot_item = [x for x in ot.get_plot().get_items() if isinstance(x, CurveItem)][2]
            ot.get_plot().select_item(ot_item)
            mock_update_all_plots_with_selection.assert_called_with(ot.get_plot())

    def test_selecting_items_in_riskmatrix_plot_update_slections_to_match_in_other_plots(self):
        nm, rm, ot = self.plot_a_random_dataset()

        risk_item = [x for x in rm.get_plot().get_items() if isinstance(x, EllipseShape)][5]
        # ^ lets select something that is also represented in the current optimaltimegraph (see plot_a_random_dataset)
        self.assertFalse(nm.get_plot().get_selected_items())
        rm.get_plot().select_item(risk_item)
        self.assertEqual(nm.get_plot().get_selected_items()[0].id_, risk_item.id_)
        self.assertEqual(ot.get_plot().get_selected_items()[0].id_, risk_item.id_)

    def test_selecting_items_in_networkmap_plot_update_slections_to_match_in_other_plots(self):
        nm, rm, ot = self.plot_a_random_dataset()

        network_item = [x for x in nm.get_plot().get_items() if isinstance(x, CurveItem)][2]
        # ^ now this curve is not represented in the optimaltimegraph (see plot_a_random_dataset)

        nm.get_plot().select_item(network_item)
        self.assertEqual(rm.get_plot().get_selected_items()[0].id_, network_item.id_)

    def test_selecting_items_in_optimaltimegraph_plot_update_slections_to_match_in_other_plots(
            self):
        nm, rm, ot = self.plot_a_random_dataset()

        ot_item = [x for x in ot.get_plot().get_items() if isinstance(x, CurveItem)][4]
        ot.get_plot().select_item(ot_item)
        self.assertEqual(nm.get_plot().get_selected_items()[0].id_, ot_item.id_)
        self.assertEqual(rm.get_plot().get_selected_items()[0].id_, ot_item.id_)

    def plot_a_random_dataset(self):
        import string
        import random
        import math
        rm = self.aw.riskmatrix
        nm = self.aw.networkmap
        ot = list(self.aw.optimaltimegraphs.values())[0]

        def id_generator(size=3, chars=string.ascii_letters + " " + string.digits):
            return ''.join(random.choice(chars) for _ in range(size))

        def plot_link(x1, y1, x2, y2, id):
            link = mock.MagicMock()
            link.start.x = x1
            link.start.y = y1
            link.end.x = x2
            link.end.y = y2
            link.vertices = []
            link.id = id
            nm.draw_links([link])

        N = 10
        x1 = np.random.rand(N) * 500
        y1 = np.random.rand(N) * 1000
        x2 = np.random.rand(N) * 500
        y2 = np.random.rand(N) * 1000
        ids = [id_generator(4) for x in range(N)]

        for i in range(N):
            plot_link(x1[i], y1[i], x2[i], y2[i], ids[i])
            rm.plot_item(ids[i], [random.random() * 15000, random.random() * 100], title=ids[i])
        for i in range(5, 8):
            years = [1997, 1998, 1999, 2005, 2008]
            val = random.random() / 10.
            ot.plotCurveSet(ids[i], years, [1000 * math.exp(val * (x - years[0]))
                                            for x in years], [1000 - 1000 * math.exp(-val * 2 * (x - years[0])) for x in years])
        return nm, rm, ot


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_main_window()
        ot.setUp()
        ot.test_selecting_items_in_riskmatrix_plot_update_slections_to_match_in_other_plots()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
