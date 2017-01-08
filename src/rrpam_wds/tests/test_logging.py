from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import sys
import time

from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import LogDialog
from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):

    def setUp(self):  # special setup for this test set.
        global start
        self.app = QApplication.instance() or QApplication(sys.argv)
        start = time.time()

    def test_creating_main_window_will_write_log_messages(self):
        self.aw = MainWindow()

        log = self.aw.logdialog.get_text()
        self.assertIn(self.aw.LOGSTARTMESSAGE, log)
        self.aw.show_logwindow()

    def test_calling_show_log_in_main_window_will_show_log_dialog(self):
        self.aw = MainWindow()
        self.assertFalse([x for x in self.aw.mdi.subWindowList()
                          if isinstance(x.widget(), LogDialog)])
        self.aw.show_logwindow()
        li = [x for x in self.aw.mdi.subWindowList() if isinstance(x.widget(), LogDialog)]
        self.assertTrue(li)
        self.assertEqual(li[0].widget(), self.aw.logdialog)

    def test_calling_show_log_multiple_times_will_not_create_multiple_windows(self):
        self.aw = MainWindow()
        self.aw.show_logwindow()
        li1 = self.aw.mdi.subWindowList()
        self.aw.show_logwindow()
        li2 = self.aw.mdi.subWindowList()
        self.assertEqual(li1, li2)

    def closing_log_window_can_be_followed_by_opening_it_again_and_same_log_window_will_reaapper(
            self):
        self.aw = MainWindow()
        self.aw.show_logwindow()
        li1 = self.aw.mdi.subWindowList()
        logdialog1 = [x for x in li1 if isinstance(x.widget(), LogDialog)][0]
        logdialog1.close()
        self.aw.show_logwindow()
        li2 = self.aw.mdi.subWindowList()
        logdialog2 = [x for x in li2 if isinstance(x.widget(), LogDialog)][0]
        self.assertEqual(logdialog1.widget(), logdialog2.widget())


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
