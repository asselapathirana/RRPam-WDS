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

    def test_risk_matrix_etc_remember_geometry(self):
        oldgeometry1 = QtCore.QRect(100, 100, 500, 500)
        self.aw.riskmatrix.parent().setGeometry(oldgeometry1)
        oldgeometry2 = QtCore.QRect(200, 150, 505, 508)
        self.aw.networkmap.parent().setGeometry(oldgeometry2)
        oldgeometry3 = QtCore.QRect(300, 200, 509, 510)
        self.aw.optimal_time_graphs()[0].parent().setGeometry(oldgeometry3)
        oldgeometry4 = QtCore.QRect(100, 300, 511, 512)
        self.aw.datawindow.parent().setGeometry(oldgeometry4)
        self.aw.show()
        # now start a new session.
        self.app.closeAllWindows()
        self.app.exit()
        self.app = None
        time.sleep(1)
        self.app = QApplication([])
        self.aw = MainWindow()
        self.assertEqual(oldgeometry1, self.aw.riskmatrix.parent().geometry())
        self.assertEqual(oldgeometry2, self.aw.networkmap.parent().geometry())
        self.assertEqual(oldgeometry3, self.aw.optimal_time_graphs()[0].parent().geometry())
        self.assertEqual(oldgeometry4, self.aw.datawindow.parent().geometry())

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
