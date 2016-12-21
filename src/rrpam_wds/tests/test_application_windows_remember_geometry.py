from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


def trigger_sub_menu_item(mainwindow, menutext, submenutext):
    filemenu = [x for x in mainwindow.menuBar().actions() if x.text() == menutext][0]
    sb = filemenu.menu()
    sm = [x for x in sb.actions() if x.text() == submenutext][0]
    sm.trigger()  # don't use toggle, use trigger.


class TC(Test_Parent):

    def test_main_window_remember_geometry(self):
        oldgeometry = QtCore.QRect(10, 10, 1000, 750)
        self.aw.setGeometry(oldgeometry)
        self.aw.close()
        # now start a new session.
        self.app.closeAllWindows()
        self.app.exit()
        self.app = None
        time.sleep(1)
        self.app = QApplication([])
        self.aw = MainWindow()
        self.assertEqual(self.aw.geometry(), oldgeometry)


if __name__ == "__main__":
    main(TC, test=False)
