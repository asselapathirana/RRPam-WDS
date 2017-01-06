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
    
    
    def test_pressing_apply_will_cause__replot_my_items_to_be_called(self):
        wlc = self.aw.get_optimal_time_graphs()[0]        
        with mock.patch.object(wlc,"_replot_my_items") as mock__replot_my_items:
            self.aw.projectgui.projectproperties.SIG_APPLY_BUTTON_CLICKED.emit()
            self.app.processEvents()
            time.sleep(1)   
            mock__replot_my_items.assert_called_once()
    
    def test_calling_replot_me_will_cause_correct_calls_to_plot_item(self):
        """Testing replot behavior"""
        self.create_a_new_project()
        self.aw.datawindow.myplotitems['111'].select()
        wlc = self.aw.get_optimal_time_graphs()[0]
        wlc._plot_selected_items()
        for th in self.aw.pm.curve_threads:
            th.wait()
        self.app.processEvents()
        time.sleep(1)        
        with mock.patch.object(wlc,"plot_item") as mock_plot_item:
            # now request replot
            wlc._replot_my_items()
            for th in self.aw.pm.curve_threads:
                th.wait()
            self.app.processEvents()
            time.sleep(.1)  
            # now we should have calls. 
            self.assertEqual(mock_plot_item.call_count,1)
        
    
    def test_deleting_a_curve_does_not_raise_exception(self):
        """Due to the following reasons sometimes CurvePlot.del_items is called multiple times with same item
        which will raise ValueError. 
        1. when we select an object, its siblings are also selected. 
        2. when we select delete, CurvePlot is asked to remove all those selected.
        3. At the same time optimaltimegraph has a method, which will trigger removing all related items (same id), 
        which in-tern call del_items again.
        
        The del_item method is monkey-patched to render this harmless. This test make sure it works!
        """
        self.create_a_new_project()
        self.aw.datawindow.myplotitems['11'].select()
        wlc = self.aw.get_optimal_time_graphs()[0]
        wlc._plot_selected_items()  
        for th in self.aw.pm.curve_threads:
            th.wait()        
        self.app.processEvents()
        time.sleep(.1)        
        plts1 = [x for x in wlc.get_plot().get_items() if hasattr(x, 'id_') and x.id_]
        # now delete a curve. 
        wlc.get_plot().select_item(wlc.myplotitems['11'][0])
        wlc.get_plot().del_items(wlc.myplotitems['11'])
        wlc.get_plot().replot()
        self.app.processEvents()
        time.sleep(.1)
        # now make sure the items are no longer there. 
        plts2 = [x for x in wlc.get_plot().get_items() if hasattr(x, 'id_') and x.id_]
        self.assertEqual(len(plts2)+3,len(plts1))

    def test_activating_PlotWLCTool_will_call__plot_selected_items(self):
        wlc = self.aw.get_optimal_time_graphs()[0]
        with mock.patch.object(wlc, "_plot_selected_items") as mock__plot_selected_items:
            tool = wlc.get_tool(PlotWLCTool)
            tool.activate()
            mock__plot_selected_items.assert_called_with()

    def test_replotting_same_id_will_not_change_number_of_curves(self):
        self.create_a_new_project()
        self.aw.datawindow.myplotitems['11'].select()
        self.aw.datawindow.myplotitems['111'].select()
        wlc = self.aw.get_optimal_time_graphs()[0]
        wlc._plot_selected_items()
        for th in self.aw.pm.curve_threads:
            th.wait()
        self.app.processEvents()
        time.sleep(.1)
        plts = [x for x in wlc.get_plot().get_items() if hasattr(x, 'id_') and x.id_]
        ds = self.aw.projectgui.projectproperties.dataset
        ds.A = .3
        ds.N = .5
        wlc._plot_selected_items()
        for th in self.aw.pm.curve_threads:
            th.wait()
        self.app.processEvents()
        time.sleep(1)
        plts2 = [x for x in wlc.get_plot().get_items() if hasattr(x, 'id_') and x.id_]
        self.assertGreater(len(plts), 0)
        self.assertEqual(len(plts), len(plts2))
        self.assertNotEqual(plts, plts2)
        self.aw.datawindow.myplotitems['121'].select()
        wlc._plot_selected_items()
        for th in self.aw.pm.curve_threads:
            th.wait()
        self.app.processEvents()
        time.sleep(1)
        plts3 = [x for x in wlc.get_plot().get_items() if hasattr(x, 'id_') and x.id_]
        self.assertEqual(len(plts2) + 3, len(plts3))

    def test_calling__plot_selected_items_will_create_WLCThreads_in_project_manager(self):
        oldt = len(self.aw.pm.curve_threads)
        self.create_a_new_project()
        self.aw.datawindow.myplotitems['11'].select()
        self.aw.datawindow.myplotitems['111'].select()
        wlc = self.aw.get_optimal_time_graphs()[0]
        wlc._plot_selected_items()
        for th in self.aw.pm.curve_threads:
            th.wait()
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
