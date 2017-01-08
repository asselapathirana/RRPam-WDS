from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA

import logging

from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    logger = logging.getLogger()

    def test__initialize_all_components_will_not_close_log_dialog(self):
        self.aw.show_logwindow()  # log dialog is visible now
        oldlog = id(self.aw.logdialog)
        oldnet = id(self.aw.networkmap)
        self.aw._initialize_all_components()
        newlog = id(self.aw.logdialog)
        newnet = id(self.aw.networkmap)
        self.assertEqual(oldlog, newlog)
        self.assertNotEqual(oldnet, newnet)


if __name__ == "__main__":
    main(TC, test=False)
