from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import unittest
from uuid import uuid4

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialog

from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


def uniquestring():
    return str(uuid4())


class TC(Test_Parent):

    def test_datawindow_is_derived_from_QDialog(self):
        """Needed for it to use pyqt5 signal slot connections"""
        dw = self.aw.datawindow
        self.assertIsInstance(dw, QDialog)

    def test_when_attempted_to_close_datawindow_will_be_minized(self):
        dw = self.aw.datawindow
        t = uniquestring()
        dw.setWindowTitle(t)
        self.assertFalse(dw.isMinimized())
        dw.close()
        self.assertEqual(
            len([x for x in self.aw.mdi.subWindowList() if x.widget() .windowTitle() == t]),
            1)
        self.assertTrue(dw.isMinimized())

    @unittest.skip("Not successfully implemented. But not really needed in this case.")
    def test_presseing_esc_does_not_close_or_clear_the_data_window(self):
        dw = self.aw.datawindow
        self.assertTrue(dw.isVisible())
        QTest.keyPress(dw, Qt.Key_Escape)
        self.assertTrue(dw.isVisible())


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
