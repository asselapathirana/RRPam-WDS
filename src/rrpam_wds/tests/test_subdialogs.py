from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import sys
import time
import unittest
import os

import mock
from PyQt5.QtWidgets import QApplication

from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.tests.test_rrpamwds_projects import trigger_sub_menu_item
from rrpam_wds.examples import networks


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

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def test_maindialog_has__appdir_value_that_indicates_to_a_creatable_writable_directory(self):
        from rrpam_wds.constants import _appdir
        import os
        if (not os.path.isdir(_appdir)):
            if (os.path.isfile(_appdir)):
                os.unlink(_appdir)
            self.mkdir_p(_appdir)
        self.assertTrue(os.path.isdir(_appdir))
        fp = os.path.join(_appdir, 'dummy.file')
        with open(fp, 'w+'):
            pass
        self.assertTrue(os.path.isfile(fp))
        os.unlink(fp)

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

    def test_clicking_save_project_as_will_call_save_project_method_in_subdialogs_project_class(
            self):
        with mock.patch.object(self.aw.projectgui, 'save_project_as', autospec=True) as mock_save_project_as:
            self.assertFalse(mock_save_project_as.called)
            trigger_sub_menu_item(
                self.aw,
                self.aw.menuitems.file,
                self.aw.menuitems.save_project_as)
            self.assertTrue(mock_save_project_as.called)

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
            
    def test_check_epanetfile_with_non_epanet_file_will_cause_an_alert_and_return_none(self):
        from PyQt5.QtWidgets import QMessageBox
        with mock.patch.object(QMessageBox,"exec_", autospec=True) as mock_exec_:
            self.assertFalse(mock_exec_.called)
            ret=self.aw.projectgui.check_epanetfile("random.inp")
            self.assertFalse(ret)
            self.assertTrue(mock_exec_.called)
            # now test a 'good' epanet file
            mock_exec_.reset_mock()
            self.assertFalse(mock_exec_.called)
            ret=self.aw.projectgui.check_epanetfile(networks[0])
            self.assertFalse(mock_exec_.called)    
            self.assertEqual(networks[0],ret)
            
    def test_calling_new_project_will_call_check_epanetfile(self):
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
            with mock.patch.object(self.aw.projectgui, 'check_epanetfile', autospec=True) as mock_check_epanetfile:
                with mock.patch.object(self.aw.projectgui, '_create_empty_project', autospec=True) as mock__create_empty_project:
                    mock__getSaveFileName2.return_value = ("tmp", '*.inp')
                    mock__create_empty_project.return_value=None
                    self.assertFalse(mock_check_epanetfile.called)
                    self.aw.projectgui.new_project()
                    self.assertTrue(mock_check_epanetfile.called)
                    self.assertTrue(mock__create_empty_project.called)
                
                
    


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
                    'test_calling_new_project_will_call_check_epanetfile')):  # test_sync
                b = getattr(tc, a)
                if(hasattr(b, '__call__')):
                    logger = logging.getLogger()
                    logger.info("calling %s **********************************" % a)
                    clt(tc, b, mainwindow)

if __name__ == "__main__":
    main(test=False)
