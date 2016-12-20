import logging

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

from rrpam_wds import hydraulic_services as hs

class ResultSet: pass


class WorkerThread(QThread):

    def __init__(self, pm, project_data):
        self.pm = pm
        self.project_data = project_data
        super(WorkerThread, self).__init__()

    def run(self):
        self.do_the_job()

    def do_the_job(self):
        self.result = self.new_project()
        if (self.incomplete_result(self.result)):
            return None
        logger = logging.getLogger()
        logger.info("Informing that I am done with calculations ...")

        self.pm.heres_a_project_signal.emit(self.result)
        
    def incomplete_result(self, r):
        try:
            for link in r.links:
                link.start.x
                link.start.y
                link.end.x
                link.end.y
                link.id
            for node in r.nodes:
                node.x
                node.y
                node.id
            return False
        except Exception as e:
            logger = logging.getLogger()
            logger.info("Exception %s" % e)
            return True
        
            
        

    def new_project(self):
        logger = logging.getLogger()
        logger.info("starting the calculations .... ")
        network=self.project_data.get_epanetfile()
        e1 = hs.pdd_service(network, coords=True, adfcalc=True)
        rs=ResultSet()
        rs.links=e1.links.values()
        rs.nodes=e1.nodes.values()
        return rs
    



class ProjectManager(QObject):

    """This is where all the 'heavy lifting' related to RRPAM-WDS project management happens.
    Almost all time-consuming actions are processesed as sperate threads.

    This means however, we can not do any GUI stuff directly in this (GUI has to run in the main thread - PyQt rule!)
    GUI stuff happens in gui.subdialogs module)
    """

    heres_a_project_signal = pyqtSignal(object)
    
    def __init__(self, project_data):
        self.project_data = project_data
        super(ProjectManager, self).__init__()    

    @pyqtSlot()
    def new_project(self):
        """Opens a project an return the result."""
        return self._new_project()

    def _new_project(self):
        self.workerthread = WorkerThread(self, self.project_data)
        self.workerthread.start()
