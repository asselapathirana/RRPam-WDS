# ^ above line is needed to make sure the path is correctly set (under frozen conditions)
import sys
import time

from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow

from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA
from rrpam_wds import setpath  # isort:skip # NOQA

TESTARG = "RUNTESTS"


def main(argv=[]):
    currentExitCode = MainWindow.EXIT_CODE_REBOOT
    while currentExitCode == MainWindow.EXIT_CODE_REBOOT:

        app = QApplication([])
        if (len(argv) > 1 and argv[1] == TESTARG):  # pragma: no cover
            # first run tests

            win = MainWindow()
            import rrpam_wds.tests.test_optimal_time_graph as og
            og.main(og.TC, test=False, mainwindow=win)
            win = None

            win = MainWindow()
            import rrpam_wds.tests.test_main_window as mw
            mw.main(mw.TC, test=False, mainwindow=win)
            win = None

            time.sleep(3)
            app.processEvents()
            time.sleep(1)

        win = MainWindow()
        win.show()
        currentExitCode = app.exec_()
        app = None
        time.sleep(0.1)

if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
