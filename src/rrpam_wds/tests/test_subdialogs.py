from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import sys
import time
import unittest

import mock
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.tests.test_rrpamwds_projects import trigger_sub_menu_item


class TestProjects(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication.instance() or QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("RRPAMWDS Projject tests")

    def tearDown(self):
        global stop
        stop = time.time()
        logger = logging.getLogger()
        logger.info("calculation took %0.2f seconds." % (stop - start))
        self.app.quit()
        self.aw = None

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""

    def test_clicking_new_project_will_call_new_project_method_in_subdialogs_project_class(self):
        with mock.patch.object(self.aw.projectgui, 'new_project', autospec=True) as mock_new_project:
            self.assertFalse(mock_new_project.called)
            trigger_sub_menu_item(self.aw, self.aw.menuitems.file, self.aw.menuitems.new_project)
            self.assertTrue(mock_new_project.called)

    def test_clicking_open_project_will_call_open_project_method_in_subdialogs_project_class(self):
        with mock.patch.object(self.aw.projectgui, 'open_project', autospec=True) as mock_open_project:
            self.assertFalse(mock_open_project.called)
            trigger_sub_menu_item(self.aw, self.aw.menuitems.file, self.aw.menuitems.open_project)
            self.assertTrue(mock_open_project.called)

    def test_clicking_save_project_will_call_save_project_method_in_subdialogs_project_class(self):
        with mock.patch.object(self.aw.projectgui, 'save_project', autospec=True) as mock_save_project:
            self.assertFalse(mock_save_project.called)
            trigger_sub_menu_item(self.aw, self.aw.menuitems.file, self.aw.menuitems.save_project)
            self.assertTrue(mock_save_project.called)

    def test_clicking_close_project_will_call_close_project_method_in_subdialogs_project_class(
            self):
        with mock.patch.object(self.aw.projectgui, 'close_project', autospec=True) as mock_close_project:
            self.assertFalse(mock_close_project.called)
            trigger_sub_menu_item(self.aw, self.aw.menuitems.file, self.aw.menuitems.close_project)
            self.assertTrue(mock_close_project.called)


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
                    'test_')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    logger = logging.getLogger()
                    logger.info("calling %s **********************************" % a)
                    clt(tc, b, mainwindow)

if __name__ == "__main__":
    main(test=False)
