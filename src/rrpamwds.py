# ^ above line is needed to make sure the path is correctly set (under frozen conditions)
import sys

from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow

from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA
from rrpam_wds import setpath  # isort:skip # NOQA


app = QApplication([])
if (len(sys.argv) > 1):  # first run tests
    import time
    win = MainWindow()
    # win.show()
    import rrpam_wds.tests.test_optimal_time_graph as og
    og.main(test=False, mainwindow=win)
    import rrpam_wds.tests.test_main_window as mw
    win = None

    win = MainWindow()
    mw.main(test=False, mainwindow=win)
    sys.argv = [sys.argv[0]]
    win = None
    time.sleep(3)
    app.processEvents()
    time.sleep(1)

win = MainWindow()
win.show()
sys.exit(app.exec_())
