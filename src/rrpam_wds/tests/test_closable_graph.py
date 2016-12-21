from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
from uuid import uuid4

from guiqwt.label import LabelItem
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from rrpam_wds.examples import examples as ex
from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.tests.test_network_map import draw_a_network
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


def uniquestring():
    return str(uuid4())


class TC(Test_Parent):

    def selection_of_any_item_with_id__will_result_in_selecting_all_items_with_that_id(self):
        e1, nwm = draw_a_network(self.aw, network=ex.networks[0])
        # select a label of a link
        lab = [x for x in nwm.get_plot().get_items() if (
            isinstance(x, LabelItem) and hasattr(x, "id_"))][3]
        nwm.get_plot().select_item(lab)
        sel = [x for x in nwm.get_plot().get_selected_items() if (hasattr(x, "id_"))]
        wid = [x for x in nwm.get_plot().get_items() if (hasattr(x, "id_") and x.id_ == lab.id_)]
        from collections import Counter
        self.assertEqual(Counter(sel), Counter(wid))

    def test_closable_graph_can_be_closed_by_user(self):
        dummytitle = uniquestring()
        title = uniquestring()
        self.dummy = CurveDialogWithClosable(wintitle=dummytitle, mainwindow=self.aw)
        self.aw.addSubWindow(self.dummy)
        self.graph = CurveDialogWithClosable(wintitle=title, mainwindow=self.aw)
        self.aw.addSubWindow(self.graph)
        self.assertNotEqual(self.graph.windowTitle, self.dummy.windowTitle)
        self.assertEqual(self.aw.mdi.subWindowList()[-1].windowTitle(), title)
        self.aw.mdi.subWindowList()[-1].close()
        self.assertEqual(
            self.aw.mdi.subWindowList()[-1].windowTitle(), dummytitle)

    def test_closable_graph_closable_false_minized(self):
        dummytitle = uniquestring()
        title = uniquestring()
        self.dummy = CurveDialogWithClosable(wintitle=dummytitle, mainwindow=self.aw)
        self.aw.addSubWindow(self.dummy)
        self.graph = CurveDialogWithClosable(wintitle=title, mainwindow=self.aw)
        self.graph.setClosable(False)
        self.aw.addSubWindow(self.graph)
        self.assertNotEqual(self.graph.windowTitle, self.dummy.windowTitle)
        self.assertEqual(self.aw.mdi.subWindowList()[-1].windowTitle(), title)
        self.assertFalse(self.aw.mdi.subWindowList()[-1].isMinimized())
        self.aw.mdi.subWindowList()[-1].close()
        self.assertEqual(self.aw.mdi.subWindowList()[-1].windowTitle(), title)
        self.assertTrue(self.aw.mdi.subWindowList()[-1].isMinimized())

    def test_presseing_esc_does_not_close_or_clear_the_closable_graph(self):
        dummytitle = uniquestring()
        title = uniquestring()
        self.dummy = CurveDialogWithClosable(wintitle=dummytitle, mainwindow=self.aw)
        self.aw.addSubWindow(self.dummy)
        self.graph = CurveDialogWithClosable(wintitle=title, mainwindow=self.aw)
        self.graph.setClosable(False)
        self.aw.addSubWindow(self.graph)
        self.aw.show()
        self.assertTrue(self.graph.isVisible())
        QTest.keyPress(self.graph, Qt.Key_Escape)
        self.assertTrue(self.graph.isVisible())


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
