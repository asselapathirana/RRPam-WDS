from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import time

import mock

from rrpam_wds.examples import networks
from rrpam_wds.project_manager import WorkerThread
from rrpam_wds.tests.test_utils import Test_Parent


class TC(Test_Parent):

    def test_progressbar_shown_and_hiddgen_when_calculations_are_done(self):
        """ TODO: This test at the moment tests only whether dialog opening and closing calls
        are made in sequence. It has to be modified to verify WHEN these are made (i.e. one
        when the calculation is starting the other when finishing. """
        ds = self.aw.projectgui.projectproperties.dataset
        with mock.patch.object(ds, "get_epanetfile", autospec=True) as mock_get_epanetfile:
            with mock.patch.object(self.aw, "_progressbar_set_", autospec=True) as mock__progressbar_set_:
                mock_get_epanetfile.return_value = networks[2]
                wt = WorkerThread(self.aw.pm, ds)
                wt.start()
                time.sleep(.01)
                self.app.processEvents()
                # now test if the dialog signal has arrived.
                # mock__progressbar_set.assert_called_with(True)
                # self.assertTrue(self.aw.progressbar.isVisible())
                wt.wait()
                self.app.processEvents()
                # now dialog should be done
                # mock__progressbar_set.assert_called_with(False)
                calls = [mock.call(True), mock.call(False)]
                mock__progressbar_set_.assert_has_calls(calls)

    def test_progressbar_shown_and_hiddgen_when_calculations_are_done_and_failed(self):
        """ TODO: This test at the moment tests only whether dialog opening and closing calls
        are made in sequence. It has to be modified to verify WHEN these are made (i.e. one
        when the calculation is starting the other when finishing. """
        ds = self.aw.projectgui.projectproperties.dataset
        with mock.patch.object(ds, "get_epanetfile", autospec=True) as mock_get_epanetfile:
            with mock.patch.object(self.aw, "_progressbar_set_", autospec=True) as mock__progressbar_set_:
                mock_get_epanetfile.return_value = networks[1]
                wt = WorkerThread(self.aw.pm, ds)
                wt.start()
                time.sleep(.01)
                self.app.processEvents()
                # now test if the dialog signal has arrived.
                # mock__progressbar_set.assert_called_with(True)
                # self.assertTrue(self.aw.progressbar.isVisible())
                wt.wait()
                self.app.processEvents()
                # now dialog should be done
                # mock__progressbar_set.assert_called_with(False)
                calls = [mock.call(True), mock.call(False)]
                mock__progressbar_set_.assert_has_calls(calls)


if __name__ == "__main__":
    tc = TC()
    tc.setUp()
    tc.test_time_the_creation_of_a_new_project_and_saving_it()
    tc.tearDown()
