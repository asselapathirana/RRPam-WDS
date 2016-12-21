from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA


from rrpam_wds.gui.custom_toolbar_items import ResetZoomTool
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):

    def test_toolbar_has_reset_zoom_tool(self):
        self.win = self.aw.new_window(mainwindow=self.aw)
        tb = self.win.get_default_toolbar()
        self.assertTrue([x for x in tb.actions() if x.text() == ResetZoomTool.TITLE])


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
