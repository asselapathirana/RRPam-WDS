from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import time

import mock

import rrpam_wds.constants as c
from rrpam_wds.examples import networks
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):

    def test_all_units_are_available(self):
        # CFS/GPM/MGD/IMGD/AFD/
        # LPS/LPM/MLD/CMH/CMD
        for u in ["LPS", "LPM", "MLD", "CMH", "CMD", ]:
            self.assertEqual(c.METERS, c.units[u][0])
            self.assertEqual(c.MM, c.units[u][1])
        for u in ["CFS", "GPM", "MGD", "IMGD", "AFD", ]:
            self.assertEqual(c.FEET, c.units[u][0])
            self.assertEqual(c.INCHES, c.units[u][1])

    def test_new_project_will_have_correct_units(self):
        ds = self.aw.projectgui.projectproperties.dataset
        self.create_a_new_project(networks[0])
        self.assertEqual(ds.lunits, "ft")
        self.assertEqual(ds.dunits, "in")
        self.create_a_new_project(networks[2])
        self.assertEqual(ds.lunits, "m")
        self.assertEqual(ds.dunits, "mm")
        self.create_a_new_project(networks[3])
        self.assertEqual(ds.lunits, "ft")
        self.assertEqual(ds.dunits, "in")

    def test_open_project_will_have_correct_units(self):
        sf = self.create_a_new_project(networks[2])
        ds = self.aw.projectgui.projectproperties.dataset

        self.aw._save_project()
        # now change values
        ds.lunits = "foo"
        ds.dunits = "bar"
        with mock.patch.object(self.aw.projectgui, '_getOpenFileName', autospec=True) as mock__getOpenFileName:
            mock__getOpenFileName.return_value = (sf, '*.rrp')
            self.aw._open_project()

        self.assertEqual(ds.lunits, c.METERS)
        self.assertEqual(ds.dunits, c.MM)

    def create_a_new_project(self, network):
        import tempfile
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(tempfile.tempdir, "xxx3xp")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (network, '*.inp')
                self.aw._new_project()
                time.sleep(.1)
                self.app.processEvents()

                # make sure the thread finishes
                self.aw.pm.wait_to_finish()
                self.app.processEvents()
                time.sleep(.1)
                return sf


if __name__ == "__main__":
    main(TC, test=False)
