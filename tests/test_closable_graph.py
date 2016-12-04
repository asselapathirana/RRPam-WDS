from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import sys
import time
import unittest

from gui_test_tools import uniquestring
from guiqwt import tests
from guiqwt.plot import CurveDialog
from PyQt5 import QtTest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from rrpam_wds.constants import units
from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import MainWindow


class mdi_graph_test(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing multi document window")
        pass

    def tearDown(self):
        global stop
        stop = time.time()
        print("\ncalculation took %0.2f seconds." % (stop - start))
        pass

    def test_closable_graph_can_be_closed_by_user(self):
        dummytitle = uniquestring()
        title = uniquestring()
        self.dummy = CurveDialogWithClosable(wintitle=dummytitle)
        self.aw.addSubWindow(self.dummy)
        self.graph = CurveDialogWithClosable(wintitle=title)
        self.aw.addSubWindow(self.graph)
        self.assertNotEqual(self.graph.windowTitle, self.dummy.windowTitle)
        self.assertEqual(self.aw.mdi.subWindowList()[-1].windowTitle(), title)
        self.aw.mdi.subWindowList()[-1].close()
        self.assertEqual(
            self.aw.mdi.subWindowList()[-1].windowTitle(), dummytitle)

    def test_closable_graph_closable_false_minized(self):
        dummytitle = uniquestring()
        title = uniquestring()
        self.dummy = CurveDialogWithClosable(wintitle=dummytitle)
        self.aw.addSubWindow(self.dummy)
        self.graph = CurveDialogWithClosable(wintitle=title)
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
        self.dummy = CurveDialogWithClosable(wintitle=dummytitle)
        self.aw.addSubWindow(self.dummy)
        self.graph = CurveDialogWithClosable(wintitle=title)
        self.graph.setClosable(False)
        self.aw.addSubWindow(self.graph)
        self.aw.show()
        self.assertTrue(self.graph.isVisible())
        QTest.keyPress(self.graph, Qt.Key_Escape)
        self.assertTrue(self.graph.isVisible())

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""
        pass

    def test_dummy(self):
        pass


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = mdi_graph_test()
        ot.setUp()
        ot.test_presseing_esc_does_not_close_or_clear_the_closable_graph()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
