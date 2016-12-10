import subprocess
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.gui.dialogs import NetworkMap
from rrpam_wds.gui.dialogs import RiskMatrix
from rrpam_wds.gui.dialogs import optimalTimeGraph

# def test_closing_a_optimal_time_graph_window_does_not_cause_error_at_exit():
    #""" See notes at: monkey_patch_guiqwt_guidata._patch_curveplot___del__

    # At the moment this test is useless.

     #"""
    # print("Running: ",[sys.executable,__file__])
    # p = subprocess.Popen([sys.executable,__file__],
                         # stdout=subprocess.PIPE,
                         # stderr=subprocess.PIPE,
                         # stdin=subprocess.PIPE)
    # output = p.communicate()
    # print("out:", output[0])
    # print("err:", output[1])

    # assert output[1]==b""
    # assert output[0]==b""
    # assert False

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
