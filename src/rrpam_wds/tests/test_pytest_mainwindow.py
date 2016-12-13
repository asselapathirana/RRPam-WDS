import subprocess
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.gui.dialogs import NetworkMap
from rrpam_wds.gui.dialogs import RiskMatrix
from rrpam_wds.gui.dialogs import optimalTimeGraph


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
    print("Boo")
    val = app.exec_()
