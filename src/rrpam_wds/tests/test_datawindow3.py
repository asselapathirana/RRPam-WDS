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

    def get_ids(self):
        l = self.aw.datawindow.get_information()[1]
        return [self.aw.datawindow._getgroupname(x[0]) for
                x in enumerate(l)]

    def get_choices(self, QComboBoxName):
        return [QComboBoxName.itemText(i) for i in range(QComboBoxName.count())]

    def test_each_assign_asset_item_has_diameter_length_and_id(self):
        self.create_a_new_project()
        for id_, item in self.aw.datawindow.myplotitems.items():
            self.assertEqual(id_, item.id_)
            self.assertEqual(item.my_id.text(), item.id_)
            self.assertEqual(item.my_dia.text(), str(item.diameter_))
            self.assertEqual(item.my_length.text(), str(item.length_))

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
