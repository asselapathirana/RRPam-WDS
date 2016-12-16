from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import random
import sys
import time
import unittest

import mock
from guiqwt.curve import CurveItem
from guiqwt.shapes import EllipseShape
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.project_manager import ProjectManager as PM


def trigger_sub_menu_item(mainwindow, menutext, submenutext):
    filemenu = [x for x in mainwindow.menuBar().actions() if x.text() == menutext][0]
    sb = filemenu.menu()
    sm = [x for x in sb.actions() if x.text() == submenutext][0]
    sm.trigger()  # don't use toggle, use trigger.


class TestProjects(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("RRPAMWDS Projject tests")

    def tearDown(self):
        global stop
        stop = time.time()
        logger = logging.getLogger()
        logger.info("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_clicking_file_new_wlc_will_create_a_new_wlc_window(self):
        """This is the test for opening and existing project. For the moment, the project details are hard-coded.
        As we implement real project opening, this test will have to change. """
        l = len(self.aw.optimaltimegraphs)
        trigger_sub_menu_item(self.aw, self.aw.menuitems.file, self.aw.menuitems.new_wlc)
        self.assertEqual(l + 1, len(self.aw.optimaltimegraphs))

    def test_clicking_file_open_will_trigger_opening_a_project(self):
        with mock.patch.object(self.aw, '_open_project', autospec=True) as mock__open_project:
            self.assertFalse(mock__open_project.called)
            trigger_sub_menu_item(self.aw, self.aw.menuitems.file, self.aw.menuitems.open_project)
            self.assertTrue(mock__open_project.called)

    def test_triggering_open_project_will_call_project_manager__open_project(self):
        # need refactoring here. The following mock is needed to avoid file open dialog to open
        # see _open_project method (copied below) in MainWindow - there is the issue!
        # def _open_project(self):
        #    self.projectgui.open_project()
        #    self._open_project_signal.emit()
        with mock.patch.object(self.aw.projectgui, "open_project", autospec=True):

            with mock.patch.object(PM, '_open_project', autospec=True) as mock__open_project:
                self.assertFalse(mock__open_project.called)
                self.aw._open_project()
                self.assertTrue(mock__open_project.called)

    def test_project_managers_open_project_will_cause_project_to_be_opend_in_main_window(
            self, other=None):
        # see run_in_a_thread
        if (other):
            self = other
        with mock.patch.object(self.aw, '_display_project', autospec=True) as mock__display_project:
            self.aw.pm.open_project()
            self.aw.pm.workerthread.wait()
            QApplication.processEvents()  # this is very important before the assertion.
            # that is because we are not testing this within the Qt's main loop.
            time.sleep(0.1)
            mock__display_project.assert_called_with(self.aw.pm.workerthread.result)

    def test_project_manager_sends_a_network_and_main_window_plots_it_correctly(self, other=None):
        # first monkey patch open_project method in self.aw.pm.workerthread object
        from rrpam_wds.project_manager import WorkerThread

        def custom_open_project(self):
            logger = logging.getLogger()
            logger.info("I am reading an epanet file")

            class emptyclass:
                pass
            result = emptyclass()
            import rrpam_wds.examples as ex
            from rrpam_wds import hydraulic_services as hs
            time.sleep(1)
            e1 = hs.pdd_service(ex.networks[0], coords=True, adfcalc=True)
            result.nodes = e1.nodes.values()
            result.links = e1.links.values()
            for link in result.links:
                link.prob = random.random() * 100.
                link.cons = (1 - link.ADF) * 1000

            return result
        # now monkey patch
        WorkerThread.open_project = custom_open_project
        self.aw.pm.open_project()
        self.aw.pm.workerthread.wait()
        self.app.processEvents()  # give some time for the gui to plot
        time.sleep(3)  # give some time for the gui to plot

        # now test
        # what were the original ids worker sent?
        _ids = [x.id for x in self.aw.pm.workerthread.result.links]

        ids = [x.id_ for x in self.aw.networkmap.get_plot().get_items() if (
            hasattr(x, "id_") and isinstance(x, CurveItem))]
        logger = logging.getLogger()
        logger.info(str(ids))
        self.assertEqual(ids, _ids)
        ids = [x.id_ for x in self.aw.riskmatrix.get_plot().get_items() if (
            hasattr(x, "id_") and isinstance(x, EllipseShape))]
        self.assertEqual(ids, _ids)

    def test_clicking_window_log_window_will_call_show_logwindow_method(self):
        with mock.patch.object(self.aw, 'show_logwindow', autospec=True) as mock_show_logwindow:
            self.assertFalse(mock_show_logwindow.called)
            trigger_sub_menu_item(self.aw, self.aw.menuitems.file, self.aw.menuitems.show_log)
            self.assertTrue(mock_show_logwindow.called)


def clt(tc, fn, mainwindow=None):
    if(not mainwindow):
        tc.setUp()
    else:
        tc.aw = mainwindow
    fn()
    if(not mainwindow):
        tc.tearDown()


def main(test=True, mainwindow=None):
    if(test):
        unittest.main(verbosity=2)
    else:
        tc = TestProjects()
        for a in dir(tc):
            if (a.startswith(
                    'test_clicking_window_log_window_will_call_show_logwindow_method')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    print("Calling %s" % a)
                    logger = logging.getLogger()
                    logger.info("calling %s **********************************" % a)
                    clt(tc, b, mainwindow)
                    print("Called %s" % a)


if __name__ == "__main__":
    main(test=False)
