from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import time

import mock

from rrpam_wds import constants as c
from rrpam_wds.examples import networks
from rrpam_wds.tests.test_utils import Test_Parent


class TC(Test_Parent):

    def create_a_new_project(self):
        import tempfile
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(tempfile.tempdir, "xxx3xp")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[3], '*.inp')
                self.aw._new_project()
                time.sleep(.1)
                self.app.processEvents()

                # make sure the thread finishes
                self.aw.pm.wait_to_finish()
                self.app.processEvents()
                time.sleep(.1)
                return sf

    def test_time_the_creation_of_a_new_project_and_saving_it(self):
        sf = self.create_a_new_project()
        self.aw._save_project()
        with mock.patch.object(self.aw.projectgui, "_getOpenFileName", autospec=True) as mock__getOpenFileName:
            mock__getOpenFileName.return_value = (sf, "*.rrp")
            self.aw._open_project()

    def test_selecting_items_in_plots(self):
        self.create_a_new_project()
        it = self.aw.riskmatrix.myplotitems['137'][0]
        self.aw.riskmatrix.get_plot().select_item(it)
        self.assertTrue(self.aw.networkmap.myplotitems['137'][0].selected)
        it = self.aw.datawindow.myplotitems['233']
        it.my_selected.setChecked(True)
        self.assertTrue(self.aw.networkmap.myplotitems['233'][0].selected)

if __name__ == "__main__":
    tc = TC()
    tc.setUp()
    tc.test_selecting_items_in_plots()
    tc.tearDown()
