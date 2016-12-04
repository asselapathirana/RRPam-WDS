from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import sys
import time
import unittest

import numpy as np
from guiqwt import tests
from guiqwt.plot import CurveDialog
from numpy.testing import assert_array_almost_equal
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs
from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import MainWindow
from rrpam_wds.gui.dialogs import NetworkMap


class test_network_map(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        self.app = QApplication(sys.argv)
        start = time.time()
        self.aw = MainWindow()
        self.aw.setWindowTitle("Testing optimal time graph")

        pass

    def tearDown(self):
        global stop
        stop = time.time()
        print("\ncalculation took %0.2f seconds." % (stop - start))
        self.aw = None
        pass

    def runTest(self):
        """ otherwise python 2.7 returns an error
        ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""
        pass

    def test_NetworkMap_is_derived_from_CurveDialogWithClosable(self):
        """NetworkMaph should be derived from CurveDialogWithClosable class"""
        nwm = NetworkMap("foo", None, None, parent=self.aw)
        self.assertIsInstance(nwm, CurveDialogWithClosable)
        self.aw.addSubWindow(nwm)

    def test_NetworkMap_has_correct_number_of_node_representations(self):
        from guiqwt.curve import CurveItem
        pdds, nodes, nwm = self.draw_a_network()
        curves = [list(zip(x.data().xData(), x.data().yData()))
                              for x in nwm.get_plot().get_items() if(isinstance(x, CurveItem))]        
        for node in nodes:
            self.assertIn([(node.x, node.y)], curves)

    def draw_a_network(self, network=ex.networks[0]):
        e1 = hs.pdd_service(network, coords=True)
        nodes = e1.nodes.values()
        links = e1.links.values()
        nwm = NetworkMap("foo", nodes, links, parent=self.aw)
        self.aw.addSubWindow(nwm)
        return e1, nodes, nwm

    def test_NetworkMap_scales_to_fit_network_on_creation(self):
        pdds, nodes, nwm = self.draw_a_network()
        coords = [(n.x, n.y) for n in nodes]
        xmin = min([x[0] for x in coords])
        xmax = max([x[0] for x in coords])
        ymin = min([x[1] for x in coords])
        ymax = max([x[1] for x in coords])
        print(xmin, xmax, ymin, ymax)
        plot = nwm.get_plot()
        _xmin, _xmax = plot.get_axis_limits("bottom")
        _ymin, _ymax = plot.get_axis_limits("left")

        self.assertAlmostEqual(xmin, _xmin, delta=5.0)
        self.assertAlmostEqual(xmax, _xmax, delta=5.0)
        self.assertAlmostEqual(ymin, _ymin, delta=5.0)
        self.assertAlmostEqual(ymax, _ymax, delta=5.0)
        pass

    def test_NetworkMap_has_correct_number_of_link_representations(self):
        for i, network in enumerate(ex.networks):
            if (i == 1):
                continue  # this is Net3.inp - it has a coordinate missing!
            from guiqwt.curve import CurveItem
            pdds, nodes, nwm = self.draw_a_network(network=network)
            links = pdds.links.values()
            curves = [list(zip(x.data().xData(), x.data().yData()))
                      for x in nwm.get_plot().get_items() if(isinstance(x, CurveItem))]

            for link in links:
                pts = link.vertices
                pts[0:0] = [(link.start.x, link.start.y)]
                pts.append((link.end.x, link.end.y))
                self.assertIn(pts, curves)


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_network_map()
        ot.setUp()
        ot.test_NetworkMap_has_correct_number_of_link_representations()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
