from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import time

import mock

import rrpam_wds.constants as c
from rrpam_wds.examples import networks
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    logger = logging.getLogger()

    def get_ids(self):
        l = self.aw.datawindow.get_information()[1]
        return [self.aw.datawindow._getgroupname(x[0]) for
                x in enumerate(l)]

    def get_choices(self, QComboBoxName):
        return [QComboBoxName.itemText(i) for i in range(QComboBoxName.count())]

    def test_group_choices_are_correctly_updated(self):
        choice = self.aw.datawindow.ui.grouptocopy
        # Check doing nothing first
        ids = self.get_ids()
        vals = self.get_choices(choice)
        self.assertEqual(ids, vals)
        # now check with extra few items added.
        dw = self.aw.datawindow.ui.no_groups
        dw.setValue(5)
        # now check again
        ids = self.get_ids()
        vals = self.get_choices(choice)
        self.assertEqual(len(vals), 5)
        self.assertEqual(ids, vals)
        # remove some items
        dw.setValue(2)
        # now check again
        ids = self.get_ids()
        vals = self.get_choices(choice)
        self.assertEqual(len(vals), 2)
        self.assertEqual(ids, vals)

    def test_selecting_assign_group_item_will_call_update_all_plots_with_selection_with_dataWindow_as_argument(
            self):
        # first create a new project
        self.create_a_new_project()
        # now test
        shs = self.aw.datawindow.myplotitems
        ids = list(self.aw.datawindow.myplotitems.keys())
        with mock.patch.object(self.aw, "update_all_plots_with_selection") as mock_update_all_plots_with_selection:
            shs[ids[2]].select()
            mock_update_all_plots_with_selection.assert_called

    def test_selecting_link_in_network_map_will_be_reflected_in_datawindow(self):
        from guiqwt.curve import CurveItem
        # first create a new project
        self.create_a_new_project()
        # now test
        cs = [self.aw.networkmap.myplotitems['10'], self.aw.networkmap.myplotitems['11']]
        cs = [item for sublist in cs for item in sublist]
        cs = [x for x in cs if isinstance(x, CurveItem)]
        self.aw.networkmap.get_plot().select_some_items(cs)
        ds = self.aw.datawindow.get_selected_items()
        self.assertEqual(sorted([x.id_ for x in ds]), sorted(['10', '11']))
        # test also deselection
        # TODO: Currently there is a bug (?) in plot windows that makes it not
        # possible to deselect part of the selection
        self.aw.networkmap.get_plot().unselect_all()
        ds = self.aw.datawindow.get_selected_items()
        self.assertEqual(ds, [])

    def test_selection_and_deselection_change_color_of_assign_assert_widgets(self):
        self.create_a_new_project()
        p = self.aw.datawindow.myplotitems['11']
        cdefault = p.my_selected.property("selected")
        p.select()
        cnew = p.my_selected.property("selected")
        self.assertNotEqual(cdefault, cnew)

    def test_my_group_initially_has_first_choice_value_selected(self):
        self.create_a_new_project()
        for item in self.aw.datawindow.myplotitems.values():
            self.assertGreater(item.my_group.count(), 0)
            self.assertEqual(item.my_group.currentIndex(), 0)
            self.assertEqual(item.my_group.currentText(), self.aw.datawindow._getgroupname(0))

    def test_if_my_groups_choice_lost_it_will_select_last_available_value(self):
        self.create_a_new_project()
        l=list(self.aw.datawindow.myplotitems.values())
        it0 = l[0].my_group
        it1 = l[1].my_group
        it2 = l[2].my_group
        it3 = l[5].my_group
        self.aw.datawindow.ui.no_groups.setValue(8)  # now we have 8 groups 0 to 7
        it0.setCurrentIndex(7)
        it1.setCurrentIndex(6)
        it2.setCurrentIndex(5)
        it3.setCurrentIndex(4)
        # now reduce choice
        self.aw.datawindow.ui.no_groups.setValue(7)
        self.assertTrue(
            it0.currentIndex() ==
            it1.currentIndex() ==
            it2.currentIndex() + 1 ==
            it3.currentIndex() + 2)
        self.aw.datawindow.ui.no_groups.setValue(6)
        self.assertTrue(
            it0.currentIndex() ==
            it1.currentIndex() ==
            it2.currentIndex() ==
            it3.currentIndex() + 1)
        self.aw.datawindow.ui.no_groups.setValue(5)
        self.assertTrue(
            it0.currentIndex() ==
            it1.currentIndex() ==
            it2.currentIndex() ==
            it3.currentIndex())

    def create_a_new_project(self):
        import tempfile
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(tempfile.tempdir, "xxx3xp")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[0], '*.inp')
                self.aw._new_project()
                time.sleep(.1)
                self.app.processEvents()

                # make sure the thread finishes
                self.aw.pm.wait_to_finish()
                self.app.processEvents()
                time.sleep(.1)


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)