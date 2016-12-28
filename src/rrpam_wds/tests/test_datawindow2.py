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

    def test_getProb_method_returns_probability(self):
        import math
        self.create_a_new_project()
        p = self.aw.datawindow.getProb('11', 0)
        dp = c.DEFAULT_N0 * math.exp(c.DEFAULT_A * 0)
        self.assertAlmostEqual(p, dp, delta=0.0001)
        p = self.aw.datawindow.getProb('11', 25)
        dp = c.DEFAULT_N0 * math.exp(c.DEFAULT_A * (25 + 0))
        self.assertAlmostEqual(p, dp, delta=0.0001)

    def test_calculate_risk_method__calls_get_prob(self):
        """Perhaps this should logically be in a different test module."""
        class EmptyClass(object):
            pass
        p = .1
        with mock.patch.object(self.aw.datawindow, "getProb", autospec=True) as mock_getProb:
            mock_getProb.return_value = p
            li = EmptyClass()
            li.ADF = .5
            li.id = 'xx'
            res = self.aw._calculate_risk([li])
            mock_getProb.assert_called_once_with(li.id, 0)
            self.assertEqual(res[0].prob, .1)
            adf = li.ADF * self.aw.projectgui.projectproperties.dataset.totalcost * \
                c.DIRECTCOSTMULTIPLIER
            self.assertEqual(res[0].cons, adf)

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

    def test_open_project_will_correctly_show_asset_groups_saved(self):

        sf, A1, N1, age1, A2, N2, age2 = self.change_some_groups_in_a_new_project()
        self.aw._save_project()
        self.create_a_new_project()  # just so that everything we set before are gone
        #
        with mock.patch.object(self.aw.projectgui, "_getOpenFileName") as mock__getOpenFileName:
            mock__getOpenFileName.return_value = (sf, "*.rrp")
            self.aw._open_project()
            d = self.aw.datawindow
            self.assertEqual(d.activenumberofgroups, 3)
            self.assertEqual(d.assetgrouplist[1].A.text(), str(A1))
            self.assertEqual(d.assetgrouplist[1].N0.text(), str(N1))
            self.assertEqual(d.assetgrouplist[1].age.value(), age1)
            self.aw.datawindow.ui.no_groups.setValue(
                5)  # we have activated 5 groups now (open hidden values we saved)
            self.assertEqual(d.assetgrouplist[3].A.text(), str(A2))
            self.assertEqual(d.assetgrouplist[3].N0.text(), str(N2))
            self.assertEqual(d.assetgrouplist[3].age.value(), age2)

    def change_some_groups_in_a_new_project(self):
        def setValues(self, i, A1, N1, age1):
            self.aw.datawindow.assetgrouplist[i].A.setText(str(A1))
            self.aw.datawindow.assetgrouplist[i].N0.setText(str(N1))
            self.aw.datawindow.assetgrouplist[i].age.setValue(age1)

        sf = self.create_a_new_project()
        # now add several property groups, set ngroups value and save
        self.aw.datawindow.ui.no_groups.setValue(5)  # we have activated 5 groups now
        A1 = .1
        N1 = .3e-1
        age1 = 25
        setValues(self, 1, A1, N1, age1)
        A2 = .2e2
        N2 = .2
        age2 = 2
        setValues(self, 3, A2, N2, age2)
        self.aw.datawindow.ui.no_groups.setValue(
            3)  # we have activated 3 groups now (4 and 5 will be saved hidden)
        return sf, A1, N1, age1, A2, N2, age2

    def test_open_project_will_correctly_show_my_group_of_each_asset(self):

        sf, A1, N1, age1, A2, N2, age2 = self.change_some_groups_in_a_new_project()
        d = self.aw.datawindow
        d.myplotitems['10'].my_group.setCurrentText(d._getgroupname(1))
        d.myplotitems['11'].my_group.setCurrentText(d._getgroupname(2))
        d.myplotitems['110'].my_group.setCurrentText(d._getgroupname(0))
        self.aw._save_project()
        self.create_a_new_project()  # just so that everything we set before are gone
        d = self.aw.datawindow
        self.assertNotEqual(d.myplotitems['10'].my_group.currentIndex(), 1)
        #
        with mock.patch.object(self.aw.projectgui, "_getOpenFileName") as mock__getOpenFileName:
            mock__getOpenFileName.return_value = (sf, "*.rrp")
            self.aw._open_project()
            # see if we have right my_group values
            d = self.aw.datawindow
            self.assertEqual(d.myplotitems['10'].my_group.currentIndex(), 1)
            self.assertEqual(d.myplotitems['11'].my_group.currentIndex(), 2)
            self.assertEqual(d.myplotitems['110'].my_group.currentIndex(), 0)

    def test_my_group_initially_has_first_choice_value_selected(self):
        self.create_a_new_project()
        for item in self.aw.datawindow.myplotitems.values():
            self.assertGreater(item.my_group.count(), 0)
            self.assertEqual(item.my_group.currentIndex(), 0)
            self.assertEqual(item.my_group.currentText(), self.aw.datawindow._getgroupname(0))

    def test_if_my_groups_choice_lost_it_will_select_last_available_value(self):
        self.create_a_new_project()
        l = list(self.aw.datawindow.myplotitems.values())
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
                return sf


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
