from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea

from rrpam_wds.gui.dialogs import NetworkMap
from rrpam_wds.gui.dialogs import RiskMatrix
from rrpam_wds.gui.dialogs import optimalTimeGraph
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class test_main_window(Test_Parent):

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
        self.aw._standard_windows()  # Adds riskmatrix, network map and a optimaltimegraph
        list1 = self.aw.mdi.subWindowList()  # should have above three
        self.aw.add_riskmatrix()  # try adding a rm
        self.aw.add_networkmap()  # try adding a nm
        self.aw._standard_windows()  # this will add only an extra optimaltimegraph
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
        self.assertEqual(len(list1), len(list2))

        for w in self.aw.mdi.subWindowList():
            self.assertTrue(w.isMinimized())

    def test_display_project_will_not_raise_exceptions_for_any_object_passed_to_it(self):
        dummy = object()
        self.aw.take_up_results(dummy)
        self.assertTrue(True)

if __name__ == "__main__":
    main(test_main_window, test=False)
