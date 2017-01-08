from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA
from rrpam_wds import setpath  # isort:skip # NOQA
# ^ above line is needed to make sure the path is correctly set (under frozen conditions)

import os
import sys

from PyQt5.Qt import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QSplashScreen

TESTARG = "RUNTESTS"
EXIT_CODE_REBOOT = 191919197


def main(argv=[]):

    currentExitCode = EXIT_CODE_REBOOT
    while currentExitCode == EXIT_CODE_REBOOT:

        app = QApplication([])

        if getattr(sys, 'frozen', False):
            # frozen
            dir_ = os.path.dirname(sys.executable)
        else:
            # unfrozen
            dir_ = os.path.dirname(os.path.realpath(__file__))

        # IMG_PATH = IMG_PATH.append(os.path.join(dir_, 'images'))

        # Create and display the splash screen
        splash_pix = QPixmap(os.path.join(dir_, './rrpam_wds/gui/images/splash_screen.png'))
        if (splash_pix is None):
            pass
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        # splash.setMask(splash_pix.mask())
        splash.show()
        import time
        start = time.time()

        while time.time() - start < .5:
            time.sleep(0.001)
            app.processEvents()

        from rrpam_wds.gui.dialogs import MainWindow

        from guidata.configtools import get_icon

        app.setWindowIcon(get_icon("main_logo.png"))
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
        if(splash):
            splash.finish(win)
        splash = None
        currentExitCode = app.exec_()
        app = None
        time.sleep(0.1)

if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
