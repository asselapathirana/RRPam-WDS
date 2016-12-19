import logging

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
        logger = logging.getLogger()
        logger.info("Emitting...")

        self.pm.heres_a_project_signal.emit(self.result)

    def open_project(self):
        logger = logging.getLogger()
        logger.info("starting the calculations .... ")
        for i in range(5):
            self.sleep(1)
            logger = logging.getLogger()
            logger.info("Tik %d " % i)
        return object()


class ProjectManager(QObject):

    """This is where all the 'heavy lifting' related to RRPAM-WDS project management happens.
    Almost all time-consuming actions are processesed as sperate threads.

    This means however, we can not do any GUI stuff directly in this (GUI has to run in the main thread - PyQt rule!)
    GUI stuff happens in gui.subdialogs module)
    """

    heres_a_project_signal = pyqtSignal(object)

    @pyqtSlot()
    def open_project(self):
        """Opens a project an return the result."""
        return self._open_project()

    def _open_project(self):
        self.workerthread = WorkerThread(self)
        self.workerthread.start()
