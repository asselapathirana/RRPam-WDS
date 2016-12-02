from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA
from rrpam_wds import setpath # isort:skip # NOQA 
# ^ above line is needed to make sure the path is correctly set (under frozen conditions)
import os
import sys
import time

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication


from rrpam_wds.cli import Main


class Tester(QObject):
    finished = pyqtSignal()
    addAWindow = pyqtSignal(int)
    timetogo = pyqtSignal()
    recordMe = pyqtSignal(str)

    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        super(Tester, self).__init__()

    @pyqtSlot()
    def do_some_testing(self):  # A slot takes no params

        for i in range(1, 11):
            time.sleep(1)
            self.addAWindow.emit(i)
            print(i)

        self.finished.emit()
        time.sleep(.1)
        # this is a hack. If this is not here, the main (gui) thread will freeze.
        # Need to find why.
        self.now_wait()

    @pyqtSlot()
    def now_wait(self):
        self.recordMe.emit("screenshot-1.jpg")
        print("Work done .. now biding time")
        for i in range(1, 11):
            time.sleep(1)
            print(11 - i)
        print(".. and done!")

        time.sleep(.1)
        QApplication.processEvents()
        if(not len(self.mainwindow.mdi.subWindowList()) == 10):
            raise Exception
        self.timetogo.emit()


if (len(sys.argv) == 1):  # plain run
    main = Main()
    sys.exit(main.app.exec_())

else:  # run as a test. Open, run tests and close.
    main = Main()
    tester = Tester(main.win)
    thread = QThread()
    tester.moveToThread(thread)
    tester.addAWindow.connect(main.win.new_window)
    #tester.recordMe.connect(main.screenshot)
    # tester.timetogo.connect(thread.quit)
    tester.finished.connect(thread.quit)
    # this is also needed to prevent gui from freezing upon finishing the
    # thread.
    thread.started.connect(tester.do_some_testing)
    tester.timetogo.connect(main.app.exit)
    thread.start()
    main.show_application()
