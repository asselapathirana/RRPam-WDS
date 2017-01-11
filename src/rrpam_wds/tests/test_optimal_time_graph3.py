from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import time

import mock

import rrpam_wds.constants as c
from rrpam_wds.examples import networks
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    logger = logging.getLogger()

    def test_asking_to_plot_multiple_wlc_curves_work(self):
        self.create_a_new_project()
        self.aw.datawindow.myplotitems['11'].select()
        self.aw.datawindow.myplotitems['111'].select()
        wlc = self.aw.get_wlc_windows()[0]
        with mock.patch.object(self.aw.pm, "callwithmyid", autospec=True) as mock_callwithmyid:
            # now call
            wlc._plot_selected_items()
            self.aw.pm.curve_thread.wait()
            self.app.processEvents()
            time.sleep(.1)
            calls = [mock.call('11'), mock.call('111')]
            mock_callwithmyid.assert_has_calls(calls, any_order=True)
            
    def test_BUG_FIX_just_changing_a_value_would_not_create_a_new_wlc_window(self):
        self.create_a_new_project()
        self.aw.datawindow.myplotitems['11'].select()    
        c=list(self.aw.optimaltimegraphs.values())[0]
        oldc=dict(c.myplotitems)
        self.aw.datawindow.myplotitems['11'].my_age.setValue(250)
        self.app.processEvents()
        time.sleep(0.1)
        newc=c.myplotitems
        self.assertEqual(oldc,newc)

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
