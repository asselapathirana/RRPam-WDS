import unittest

import mock
import rrpamwds
from PyQt5.QtWidgets import QApplication

import rrpam_wds.tests.test_main_window as mw
from rrpam_wds.gui.dialogs import MainWindow


class TC(unittest.TestCase):

    def test_main_applcation_script(self):
        with mock.patch.object(QApplication, "exec_") as mock_exec_:
                with mock.patch.object(MainWindow, "show") as mock_show:
                    rrpamwds.main()
                    mock_exec_.assert_called()
                    mock_show.assert_called()

    def test_calling_main_application_with_TESTARG_will_call_tests(self):
        with mock.patch.object(QApplication, "exec_"):
            with mock.patch.object(mw.TC, "test_mainwindow_has_a_mdi_Area") as mock_test:
                rrpamwds.main()
                mock_test.assert_not_called()
                rrpamwds.main(["", rrpamwds.TESTARG])
                mock_test.assert_called()
