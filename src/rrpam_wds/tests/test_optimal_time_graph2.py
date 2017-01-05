from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import time

import mock

import rrpam_wds.constants as c
from rrpam_wds.examples import networks
from rrpam_wds.gui.custom_toolbar_items import PlotWLCTool
from rrpam_wds.project_manager import WLCThread
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    logger = logging.getLogger()

    def test_activating_PlotWLCTool_will_call__plot_selected_items(self):
        wlc = self.aw.get_optimal_time_graphs()[0]
        with mock.patch.object(wlc, "_plot_selected_items") as mock__plot_selected_items:
            tool = wlc.get_tool(PlotWLCTool)
            tool.activate()
            mock__plot_selected_items.assert_called_with()

    def test_calling__plot_selected_items_will_create_WLCThreads_in_project_manager(self):
        oldt = len(self.aw.pm.curve_threads)
        self.create_a_new_project()
        self.aw.datawindow.myplotitems['11'].select()
        self.aw.datawindow.myplotitems['111'].select()
        wlc = self.aw.get_optimal_time_graphs()[0]
        wlc._plot_selected_items()
        self.app.processEvents()
        time.sleep(1)
        newt = self.aw.pm.curve_threads
        self.assertEqual(oldt + 2, len(newt))
        for item in newt:
            self.assertIsInstance(item, WLCThread)

    def test_starting_WLCThread_will_call__plot_wlc_upon_finishing(self):
        wlct = WLCThread(self.aw.pm, c.WLCData())
        with mock.patch.object(self.aw, "_plot_wlc_") as mock__plot_wlc_:
            wlct.run()  # yes, we are calling the run method directly for testing
            # (in code this should be start())
            mock__plot_wlc_.assert_called_with(wlct.result)

    def test_plot_calculator_will_call_pm_calculate_curves_once_for_each_selected_asset(self):
        self.create_a_new_project()
        with mock.patch.object(self.aw.pm, "calculate_curves") as mock_calculate_curves:
            a1 = self.aw.datawindow.myplotitems['11']
            a2 = self.aw.datawindow.myplotitems['111']
            a3 = self.aw.datawindow.myplotitems['121']
            a1.select()
            a2.select()
            a3.select()
            self.aw.call_plot_calculator("X#)()(KDJLKLKa")
            calls = [mock.call(a1.get_curve_data()),
                     mock.call(a2.get_curve_data()),
                     mock.call(a3.get_curve_data())]
            mock_calculate_curves.has_calls(calls)

    def test_wlc_window_requesting_plots_will_get_wlc_curves(self):
        self.create_a_new_project()
        self.aw.add_optimaltimegraph()
        self.aw.add_optimaltimegraph()
        # now we have 3 wlc windows
        wlcw = self.aw.get_optimal_time_graphs()
        a1 = self.aw.datawindow.myplotitems['11']
        a2 = self.aw.datawindow.myplotitems['111']
        a3 = self.aw.datawindow.myplotitems['121']
        a1.select()
        a2.select()
        a3.select()
        with mock.patch.object(wlcw[0], "plot_item") as mock_plot_item:
            wlcw[0]._plot_selected_items()
            self.app.processEvents()
            time.sleep(0.1)
            for th in self.aw.pm.curve_threads:
                th.wait()
            # now assert
            self.app.processEvents()
            time.sleep(0.1)
            self.assertEqual(len(mock_plot_item.call_args_list), 3)

        a1.select(False)
        a2.select(False)
        a3.select()

        with mock.patch.object(wlcw[1], "plot_item") as mock_plot_item:
            wlcw[1]._plot_selected_items()
            self.app.processEvents()
            time.sleep(0.1)
            for th in self.aw.pm.curve_threads:
                th.wait()
            # now assert
            self.app.processEvents()
            time.sleep(0.1)
            self.assertEqual(len(mock_plot_item.call_args_list), 1)
            a1.select(False)
            a2.select(False)

    def create_a_new_project(self):
        import tempfile
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(tempfile.tempdir, "xxx3xp")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[0], '*.inp')
                self.aw._new_project()
                time.sleep(.1)
                self.app.processEvents()

                # make sure the thread finishes
                self.aw.pm.wait_to_finish()
                self.app.processEvents()
                time.sleep(.1)
                return sf


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)