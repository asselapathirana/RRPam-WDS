from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import errno
import logging
import os

import mock

from rrpam_wds.examples import networks
from rrpam_wds.tests.test_rrpamwds_projects import trigger_sub_menu_item
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):

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
            with mock.patch.object(self.aw.pm, '_new_project'):
                self.assertFalse(mock_new_project.called)
                trigger_sub_menu_item(
                    self.aw,
                    self.aw.menuitems.file,
                    self.aw.menuitems.new_project)
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
        with mock.patch.object(QMessageBox, "exec_", autospec=True) as mock_exec_:
            self.assertFalse(mock_exec_.called)
            ret = self.aw.projectgui.check_epanetfile("random.inp")
            self.assertFalse(ret)
            self.assertTrue(mock_exec_.called)
            # now test a 'good' epanet file
            mock_exec_.reset_mock()
            self.assertFalse(mock_exec_.called)
            ret = self.aw.projectgui.check_epanetfile(networks[0])
            self.assertFalse(mock_exec_.called)
            self.assertEqual(networks[0], ret)

    def test_calling_new_project_will_call_check_epanetfile(self):
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
            with mock.patch.object(self.aw.projectgui, 'check_epanetfile', autospec=True) as mock_check_epanetfile:
                with mock.patch.object(self.aw.projectgui, '_create_empty_project', autospec=True) as mock__create_empty_project:
                    mock__getSaveFileName2.return_value = ("tmp", '*.inp')
                    mock__create_empty_project.return_value = None
                    mock_check_epanetfile.return_value = False # so that new project creation will stop after check_epanet call. 
                    self.assertFalse(mock_check_epanetfile.called)
                    self.aw.projectgui.new_project()
                    self.assertTrue(mock_check_epanetfile.called)
                    

    def test_set_network_takes_only_ResultSet_objects(self):
        from rrpam_wds.constants import ResultSet
        logger = logging.getLogger()
        logger.info(
            "**** There will be some WARNINGS below. Don't worry (we are just testing :-) )")
        ds = self.aw.projectgui.projectproperties.dataset
        self.assertFalse(ds.results)
        ds.set_network(None)
        self.assertFalse(ds.results)
        ds.set_network(Exception())
        self.assertFalse(ds.results)
        ds.set_network(ResultSet())
        self.assertTrue(ds.results)

    def test_calling_new_file_will_update_gui_from_data_not_otherway_around(self):
        def fn(mock_set, mock_get):
            self.assertFalse(mock_set.called)
            self.assertFalse(mock_get.called)
            self.aw.projectgui.new_project()
            self.assertFalse(mock_set.called)
            self.assertTrue(mock_get.called)
        self.run_in_total_mock_context(fn)

    def test_calling_open_project_will_update_gui_from_data_not_otherway_around(self):
        def fn(mock_set, mock_get):
            self.assertFalse(mock_set.called)
            self.assertFalse(mock_get.called)
            self.aw.projectgui.open_project()
            self.assertFalse(mock_set.called)
            self.assertTrue(mock_get.called)
        self.run_in_total_mock_context(fn)

    def test_calling_new_project_will_update_gui_from_data_not_otherway_around(self):
        def fn(mock_set, mock_get):
            self.assertFalse(mock_set.called)
            self.assertFalse(mock_get.called)
            self.aw.projectgui.new_project()
            self.assertFalse(mock_set.called)
            self.assertTrue(mock_get.called)
        self.run_in_total_mock_context(fn)

    def test_calling_save_project_will_update_gui_from_data_not_otherway_around(self):
        def fn(mock_set, mock_get):
            self.assertFalse(mock_set.called)
            self.assertFalse(mock_get.called)
            self.aw.projectgui.save_project()
            self.assertTrue(mock_set.called)
            self.assertFalse(mock_get.called)
        self.run_in_total_mock_context(fn)

    def test_calling_save_project_as_will_update_gui_from_data_not_otherway_around(self):
        def fn(mock_set, mock_get):
            self.assertFalse(mock_set.called)
            self.assertFalse(mock_get.called)
            self.aw.projectgui.save_project_as()
            self.assertTrue(mock_set.called)
            self.assertFalse(mock_get.called)
        self.run_in_total_mock_context(fn)

    def run_in_total_mock_context(self, f):
        with mock.patch.object(self.aw.projectgui,
                               '_getSaveFileName',
                               autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui,
                                   '_getSaveFileName2',
                                   autospec=True) as mock__getSaveFileName2:
                with mock.patch.object(self.aw.projectgui,
                                       '_getOpenFileName',
                                       autospec=True) as mock__getOpenFileName:
                    with mock.patch.object(self.aw.projectgui,
                                           'check_epanetfile',
                                           autospec=True) as mock_check_epanetfile:
                        with mock.patch.object(self.aw.projectgui,
                                               '_create_empty_project',
                                               autospec=True) as mock__create_empty_project:

                            with mock.patch.object(self.aw.projectgui.projectproperties,
                                                   'set',
                                                   autospec=True) as mock_set:
                                with mock.patch.object(self.aw.projectgui.projectproperties,
                                                       'get',
                                                       autospec=True) as mock_get:
                                    with mock.patch.object(self.aw.projectgui,
                                                           '_valid_project',
                                                           autospec=True) as mock__valid_project:
                                        with mock.patch.object(self.aw.projectgui,
                                                               '_save_project_to_dest',
                                                               autospec=True) as mock__save_project_to_dest:
                                            with mock.patch.object(self.aw.pm,
                                                                   '_new_project',
                                                                   autospec=True):

                                                mock__getSaveFileName.return_value = (
                                                    "xxes", '*.rrp')
                                                mock__getSaveFileName2.return_value = (
                                                    "tmp.inp", '*.inp')
                                                mock__create_empty_project.return_value = 'bo'
                                                mock__getOpenFileName.return_value = (
                                                    "gox", "*.rrp")
                                                mock_check_epanetfile.return_value = "tmp.inp"
                                                mock__valid_project.return_value = True
                                                mock__save_project_to_dest.return_value = "some project"
                                                f(mock_set, mock_get)


if __name__ == "__main__":
    main(TC, test=False)
