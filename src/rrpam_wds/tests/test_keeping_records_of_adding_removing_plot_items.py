from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA

import mock
from guiqwt.curve import CurveItem
from guiqwt.shapes import EllipseShape

from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):

    def test_riskmatrix_report_adding_to_the_register(self):
        rm = self.aw.riskmatrix

        with mock.patch.object(rm, 'add_plot_item_to_record', autospec=True) as mock_add_plot_item_to_record:
            self.assertFalse(mock_add_plot_item_to_record.called)
            rm.plot_item("fox", [5000, 50], title="fox")
            self.assertTrue(mock_add_plot_item_to_record.called)

    def test_riskmatrix_report_removing_to_the_register(self):
        rm = self.aw.riskmatrix

        with mock.patch.object(rm, 'remove_plot_item_from_record', autospec=True) as mock_remove_plot_item_from_record:
            self.assertFalse(mock_remove_plot_item_from_record.called)
            rm.plot_item("fox", [5000, 50], title="fox")
            self.assertFalse(mock_remove_plot_item_from_record.called)
            risk_item = [x for x in rm.get_plot().get_items() if isinstance(x, EllipseShape)][0]
            rm.get_plot().del_item(risk_item)
            self.assertTrue(mock_remove_plot_item_from_record.called)

    def test_networkmap_report_adding_to_the_register(self):
        otg = self.aw.networkmap

        with mock.patch.object(otg, 'add_plot_item_to_record', autospec=True) as mock_add_plot_item_to_record:
            self.assertFalse(mock_add_plot_item_to_record.called)
            otg.plot_item("fox", [(5, 10), (8, 3), (24, 1)], "fox")
            self.assertTrue(mock_add_plot_item_to_record.called)

    def test_networkmap_report_removing_to_the_register(self):
        otg = self.aw.networkmap

        with mock.patch.object(otg, 'remove_plot_item_from_record', autospec=True) as mock_remove_plot_item_from_record:
            self.assertFalse(mock_remove_plot_item_from_record.called)
            otg.plot_item("fox", [(5, 10), (8, 3), (24, 1)], "fox")
            self.assertFalse(mock_remove_plot_item_from_record.called)
            nw_item = [x for x in otg.get_plot().get_items() if isinstance(x, CurveItem)][0]
            otg.get_plot().del_item(nw_item)
            self.assertTrue(mock_remove_plot_item_from_record.called)

    def test_optimaltimegraph_report_adding_to_the_register(self):
        otg = list(self.aw.optimaltimegraphs.values())[0]

        with mock.patch.object(otg, 'add_plot_item_to_record', autospec=True) as mock_add_plot_item_to_record:
            self.assertFalse(mock_add_plot_item_to_record.called)
            otg.plot_item(
                "fox", [[1997, 1998, 2005, 2008], [5, 10, 25, 95], [100, 50, 25, 12]], "fox")
            self.assertTrue(mock_add_plot_item_to_record.called)

    def test_optimaltimegraph_report_removing_to_the_register(self):
        otg = list(self.aw.optimaltimegraphs.values())[0]

        with mock.patch.object(otg, 'remove_plot_item_from_record', autospec=True) as mock_remove_plot_item_from_record:
            self.assertFalse(mock_remove_plot_item_from_record.called)
            otg.plot_item(
                "fox", [[1997, 1998, 2005, 2008], [5, 10, 25, 95], [100, 50, 25, 12]], "fox")
            self.assertFalse(mock_remove_plot_item_from_record.called)
            nw_item = [x for x in otg.get_plot().get_items() if isinstance(x, CurveItem)][0]
            otg.get_plot().del_item(nw_item)
            self.assertTrue(mock_remove_plot_item_from_record.called)

    def test_deleting_a_curve_in_optimaltimegraph_removes_all_three_curves(self):
        # for the heck of it add another optimal time graph
        self.aw.add_optimaltimegraph()
        l = list(self.aw.optimaltimegraphs.values())
        otg1 = l[0]
        otg2 = l[1]
        self.assertEqual(len(otg1.myplotitems), 0)
        otg1.plot_item("fox", [[1997, 1998, 2005, 2008], [5, 10, 25, 95], [100, 50, 25, 12]], "fox")
        otg2.plot_item("fox", [[1997, 1998, 2005, 2008], [5, 10, 25, 95], [100, 50, 25, 12]], "fox")
        self.assertEqual(len(otg1.myplotitems), 1)
        self.assertEqual(len(otg2.myplotitems), 1)
        otg_item = [x for x in otg1.get_plot().get_items() if isinstance(x, CurveItem)][0]
        otg1.get_plot().del_item(otg_item)
        self.assertEqual(len(otg1.myplotitems), 0)
        otg_item = [x for x in otg2.get_plot().get_items() if isinstance(x, CurveItem)][
            2]  # pick a different curve from the set!
        otg2.get_plot().del_item(otg_item)
        self.assertEqual(len(otg2.myplotitems), 0)


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
