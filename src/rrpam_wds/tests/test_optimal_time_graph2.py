from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import time

import mock

import rrpam_wds.constants as c
from rrpam_wds.examples import networks
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main
from rrpam_wds.gui.custom_toolbar_items import PlotWLCTool


class TC(Test_Parent):
    logger = logging.getLogger()

    def test_activating_PlotWLCTool_will_call__plot_selected_items(self):
        wlc=self.aw.get_optimal_time_graphs()[0]
        with mock.patch.object(wlc,"_plot_selected_items") as mock__plot_selected_items:
            tool=wlc.get_tool(PlotWLCTool)
            tool.activate()
            mock__plot_selected_items.assert_called_with()
        
        
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
