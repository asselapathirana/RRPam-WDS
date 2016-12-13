from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot


class WorkerThread(QThread):

    def __init__(self, pm):
        self.pm = pm
        super(WorkerThread, self).__init__()

    def run(self):
        self.do_the_job()

    def do_the_job(self):
        self.result = self.open_project()
        print("Emitting...")

        self.pm.heres_a_project_signal.emit(self.result)

    def open_project(self):
        print("starting.... ")
        for i in range(5):
            self.sleep(1)
            print("Tik ", i)
        return object()


class ProjectManager(QObject):

    """This is where all the 'heavy lifting' related to RRPAM-WDS project management happens.
    Almost all time-consuming actions are processesed as sperate threads"""

    heres_a_project_signal = pyqtSignal(object)

    @pyqtSlot()
    def open_project(self):
        """Opens a project an return the result."""
        return self._open_project()

    def _open_project(self):
        self.workerthread = WorkerThread(self)
        self.workerthread.start()