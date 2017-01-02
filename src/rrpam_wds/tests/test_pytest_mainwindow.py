import logging
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow


def test_dummy():
    assert 1 == 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    aw = MainWindow()
    aw.add_optimaltimegraph()

    for w in aw.mdi.subWindowList():
        w.close()
    # following should not raise exceptions
    aw.show()
    aw.deleteLater()
    QTimer.singleShot(5000, app.quit)  # Make the application quit just after start
    logger = logging.getLogger()
    logger.info("Boo")
    val = app.exec_()
