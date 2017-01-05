from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA

import time

from guiqwt.label import LabelItem
from guiqwt.shapes import EllipseShape

from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import RiskMatrix
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    
    def test_risk_matrix_items_store_total_cost(self):
        """Storing the total cost is important to correctly recalculate ellipses when 
        the value of 'direct cost of total system down' (totalcost) is changed"""
        self.test_plot_item_will_create_a_circle()
        ds=self.aw.projectgui.projectproperties.dataset
        mpi=self.rm.myplotitems
        self.assertGreater(len(mpi),0)
        for item in mpi.values():
            for i in item:
                self.assertEqual(ds.totalcost, i.totalcost)
       
    def test_consequence_is_recalculated_when_totalcost_is_changed(self):
        self.test_plot_item_will_create_a_circle()
        cons1 = [x.get_center()[0] for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        ds=self.aw.projectgui.projectproperties.dataset
        tc1=ds.totalcost
        ds.totalcost=tc1*10
        self.aw.projectgui.projectproperties.SIG_APPLY_BUTTON_CLICKED.emit()
        self.app.processEvents()
        time.sleep(0.1)
        cons2 = [x.get_center()[0] for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.assertEqual([x*10 for x in cons1],cons2)
            

    def test_Risk_Map_is_derived_from_CurveDialogWithClosable(self):
        self.rm = self.aw.riskmatrix
        isinstance(self.rm, CurveDialogWithClosable)

    def test_plot_item_will_create_a_circle(self):
        self.rm = self.aw.riskmatrix
        # self.aw.addSubWindow(self.rm)
        # self.rm.show()
        pts0 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.draw_some_circles()
        pts1 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.assertEqual(len(pts1), len(pts0) + 4)
        self.assertEqual(pts1[1].get_xdiameter(), self.rm.get_ellipse_xaxis(1000., 20.))

    def test_plot_item_will_create_two_entitites_circle_and_label_each_with_id_(self):
        self.rm = self.aw.riskmatrix

        pts0 = [x for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        self.draw_some_circles()
        pts1 = [x.id_ for x in self.rm.get_plot().get_items() if isinstance(x, EllipseShape)]
        labs = [x.id_ for x in self.rm.get_plot().get_items() if isinstance(x, LabelItem)]
        self.assertEqual(pts1.sort(), labs.sort())
        self.assertEqual(len(pts1), len(pts0) + 4)

    def draw_some_circles(self):
        self.rm.plot_item("foo", [5000.0, 50], title="foo")
        self.rm.plot_item("bar", [1000.0, 20], title="bar")
        self.rm.plot_item("bax", [8000.0, 70], title="bax")
        self.rm.plot_item("baxt", [15000.0, 100], title="bax")


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
