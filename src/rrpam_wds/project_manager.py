import logging

import numpy as np
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot

from rrpam_wds import hydraulic_services as hs
from rrpam_wds.constants import ResultSet
from rrpam_wds.constants import WLCCurve
from rrpam_wds.constants import _getProb


class WLCThread(QThread):

    def __init__(self, pm, project_data):
        self.pm = pm
        self.project_data = project_data
        super(WLCThread, self).__init__()

    def run(self):
        self.pm.i_start_calculations.emit(True)
        self.do_the_job()
        self.pm.i_start_calculations.emit(False)

    def do_the_job(self):
        logger = logging.getLogger()
        logger.info("Starting calculation WLCThread..")
        self.result = WLCCurve()
        self.result.requestingcurve = self.project_data.requestingcurve
        self.result.id_=self.project_data.id
        self._calculate()
        self.pm.heres_a_curve_signal.emit(self.result)
        self.sleep(1)

    def _calculate(self):
        d = self.project_data
        r = self.result
        r.year = np.arange(0, d.years, 1)
        r.renewalcost = d.cost * np.exp(-r.year * d.r / 100.)
        tmp = _getProb(d.A, r.year, d.lunits, d.N0, d.length, d.age)
        dc = tmp * np.exp(-d.r / 100. * r.year) * d.cons
        r.damagecost = np.add.accumulate(dc)


class WorkerThread(QThread):

    def __init__(self, pm, project_data):
        self.pm = pm
        self.project_data = project_data
        super(WorkerThread, self).__init__()

    def run(self):
        self.pm.i_start_calculations.emit(True)
        self.do_the_job()
        self.pm.i_start_calculations.emit(False)

    def do_the_job(self):

        logger = logging.getLogger()
        self.result = self.new_project()
        logger.info("..got the results")
        if (self.incomplete_result(self.result)):
            logger.info("ERROR: But incomplete results")
            return None

        logger.info("Informing that I am done with calculations ...")
        self.pm.heres_a_project_signal.emit(self.result)
        self.sleep(1)

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
            logger.info("Exception (a): %s" % e)
            return True

    def new_project(self):
        logger = logging.getLogger()

        network = self.project_data.get_epanetfile()
        logger.info("EPANETFILE: %s; starting the calculations .... " % network)
        if(not network):
            logger.warn("I did not get an epanet network file. I quit.")
            return None
        logger.info(".. with epanet file: %s " % network)
        try:
            e1 = hs.pdd_service(network, coords=True, adfcalc=True)
        except Exception as e:
            logger.exception("There was an error in calculations: %s" % e)
            return e
        rs = ResultSet()
        rs.units = e1.units
        rs.links = list(e1.links.values())
        rs.nodes = list(e1.nodes.values())
        rs.links[0]
        rs.nodes[0]
        logger.info(
            "Sending results set with UNITS: %s; %d nodes and %d links" %
            (rs.units, len(rs.nodes), len(rs.links)))
        return rs


class ProjectManager(QObject):

    """This is where all the 'heavy lifting' related to RRPAM-WDS project management happens.
    Almost all time-consuming actions are processesed as sperate threads.

    This means however, we can not do any GUI stuff directly in this (GUI has to run in the main thread - PyQt rule!)
    GUI stuff happens in gui.subdialogs module)
    """
    i_start_calculations = pyqtSignal(object)
    heres_a_project_signal = pyqtSignal(object)
    heres_a_curve_signal = pyqtSignal(object)

    def __init__(self, project_data):
        self.project_data = project_data
        super(ProjectManager, self).__init__()
        self.curve_threads = []

    @pyqtSlot()
    def new_project(self):
        """Opens a project an return the result."""
        return self._new_project()

    def _new_project(self):
        self.workerthread = WorkerThread(self, self.project_data)
        self.workerthread.start()

    def calculate_curves(self, wlcdata):
        """Calculates WLC curves from data provided."""

        logger = logging.getLogger()
        logger.info("I start WLC calculations for %s" % wlcdata)

        self.curve_threads.append(WLCThread(self, wlcdata))
        self.curve_threads[-1].start()

    def wait_to_finish(self):
        """if worker thread is running. this will casue the calling program to wait."""
        logger = logging.getLogger()
        logger.info("Waiting for  the calculations  to finish.... ")
        if(hasattr(self, 'workerthread')):
            self.workerthread.wait()
        logger.info("... done! ")
