from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA

from guiqwt.plot import CurveDialog

from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):

    def test_graph_window_properly_added_to_MDI(self):
        self.graph = CurveDialog(
            wintitle="XXX YYH #DKLJLKFE Kadk #kdfd", icon="guiqwt.svg",
            edit=False,
            toolbar=True,
            options=None,
            parent=self.aw,
            panels=None)

        self.aw.addSubWindow(self.graph)
        self.assertEqual(self.aw.mdi.subWindowList()[
                         -1].windowTitle(), self.graph.windowTitle())

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
