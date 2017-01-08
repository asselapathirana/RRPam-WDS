from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import time

import mock

from rrpam_wds import constants as c
from rrpam_wds.examples import networks
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


def trigger_sub_menu_item(mainwindow, menutext, submenutext):
    filemenu = [x for x in mainwindow.menuBar().actions() if x.text() == menutext][0]
    sb = filemenu.menu()
    sm = [x for x in sb.actions() if x.text() == submenutext][0]
    sm.trigger()  # don't use toggle, use trigger.


class TC(Test_Parent):

    def test_clicking_file_new_and_wait_for_datawindow_to_be_displayed(self):
        self.test_clicking_file_new_and_wait_for_network_to_be_displayed()
        idthings = [x for x in self.aw.datawindow.get_plot().get_items()
                    if hasattr(x, "id_")]
        self.assertGreater(len(idthings), 5)

    def test_clicking_file_new_and_wait_for_risk_matrix_to_be_displayed(self):
        self.test_clicking_file_new_and_wait_for_network_to_be_displayed()
        idthings = [x for x in self.aw.riskmatrix.get_plot().get_items()
                    if hasattr(x, "id_")]
        self.assertGreater(len(idthings), 5)

    def test_clicking_file_new_and_wait_for_network_to_be_displayed(self):
        """This is the test for opening and existing project. For the moment, the project details are hard-coded.
        As we implement real project opening, this test will have to change. """
        import tempfile
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(tempfile.tempdir, "xxx3xp")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[0], '*.inp')
                time.sleep(.1)
                self.app.processEvents()
                idthings = [x for x in self.aw.networkmap.get_plot().get_items()
                            if hasattr(x, "id_")]
                self.assertEqual(0, len(idthings))
                # now we can non-interactively test new_project.
                trigger_sub_menu_item(
                    self.aw,
                    self.aw.menuitems.file,
                    self.aw.menuitems.new_project)
                time.sleep(.1)
                self.app.processEvents()
                # make sure the thread finishes
                self.aw.pm.wait_to_finish()
                # but give some time for gui to plot too.
                self.app.processEvents()
                time.sleep(1)
                idthings = [x for x in self.aw.networkmap.get_plot().get_items()
                            if hasattr(x, "id_")]
                self.assertGreater(len(idthings), 5)


if __name__ == "__main__":
    main(TC, test=False)
