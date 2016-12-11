from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import os
import sys
import time
import unittest

import numpy as np
from guiqwt import tests
from guiqwt.plot import CurveDialog
from numpy.testing import assert_array_almost_equal
from PyQt5.QtCore import QPoint
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
        nwm = NetworkMap(name="foo", nodes=None, links=None, parent=self.aw, mainwindow=self.aw)
        self.assertIsInstance(nwm, CurveDialogWithClosable)
        self.aw.addSubWindow(nwm)

    def test_NetworkMap_has_correct_number_of_node_representations(self):
        from guiqwt.curve import CurveItem
        pdds, nodes, nwm = self.draw_a_network()
        curves = [list(zip(x.data().xData(), x.data().yData()))
                  for x in nwm.get_plot().get_items() if(isinstance(x, CurveItem))]
        for node in nodes:
            self.assertIn([(node.x, node.y), (node.x, node.y)], curves)
            # ^ why we represent a node with two identical coordinates?
            # see dialogs.draw_nodes function to know why

    def draw_a_network(self, network=ex.networks[0]):
        e1 = hs.pdd_service(network, coords=True, adfcalc=False)
        nodes = e1.nodes.values()
        links = e1.links.values()
        nwm = NetworkMap(name="foo", nodes=nodes, links=links, parent=self.aw, mainwindow=self.aw)
        self.aw.addSubWindow(nwm)
        self.aw.show()

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
        delta = 20.
        self.assertAlmostEqual(xmin - delta, _xmin, delta=delta)
        self.assertAlmostEqual(xmax + delta, _xmax, delta=delta)
        self.assertAlmostEqual(ymin - delta, _ymin, delta=delta)
        self.assertAlmostEqual(ymax + delta, _ymax, delta=delta)
        pass

    def test_NetworkMap_has_correct_number_of_link_representations(self):
        for i, network in enumerate(ex.networks[0:1]):  # only one network to make it fast
            if (i == 1):
                continue  # this is Net3.inp - it has a coordinate missing!
            from guiqwt.curve import CurveItem
            pdds, nodes, nwm = self.draw_a_network(network=network)
            links = pdds.links.values()
            # curves = [list(zip(x.data().xData(), x.data().yData()))
            #          for x in nwm.get_plot().get_items() if(isinstance(x, CurveItem))]
            curve_ends = [((c.data().xData()[0], c.data().yData()[0]),
                           (c.data().xData()[-1], c.data().yData()[-1]))
                          for c in nwm.get_plot().get_items() if(isinstance(c, CurveItem))]
            for link in links:
                # pts = link.vertices
                # pts[0:0] = [(link.start.x, link.start.y)]
                # pts.append((link.end.x, link.end.y))
                # Just get the two ends and check its in one of the curves.
                pts = ((link.start.x, link.start.y), (link.end.x, link.end.y))
                self.assertIn(pts, curve_ends)

    def clicking_close_to_a_link_will_select_it_on_the_plot(self):

        pdds, nodes, nwm = self.draw_a_network(network=ex.networks[0])
        # select a link
        l = pdds.links[3]
        pos = [(l.start.x + l.end.x) / 2.0, (l.start.y, l.end.y) / 2.0]
        curve = [x for x in nwm.get_plot().get_items() if x.title().text() == l.id][0]
        plot = curve.plot()
        ax = curve.xAxis()
        ay = curve.yAxis()
        px = plot.transform(ax, pos[0])
        py = plot.transform(ay, pos[1])
        print(pos[0], pos[1], px, py, curve.title().text())
        QTest.mouseClick(plot, Qt.RightButton, pos=QPoint(px, py), delay=10.)
        print(plot.get_selected_items())
        print(nwm.get_plot().get_selected_items())
        # this test does not work yet.
        # todo: fix this test to work.

    def test_Network_Map_correctly_reports_selected_links(self):
        import rrpam_wds.gui.utils as u
        pdds, nodes, nwm = self.draw_a_network(network=ex.networks[0])
        # select a link
        l = pdds.links[3]
        t = u.get_title(l)
        curve = [x for x in nwm.get_plot().get_items() if x.title().text() == t][0]
        plot = curve.plot()
        curve.select()
        self.assertEqual(len(plot.get_selected_items()), 1)
        self.assertEqual(plot.get_selected_items()[0].title().text(), t)

    def test_Network_map_item_list_has_correct_icons(self):
        import rrpam_wds.gui.utils as u
        from guiqwt.curve import CurveItem
        pdds, nodes, nwm = self.draw_a_network(network=ex.networks[2])
        # select a link
        l = pdds.links[3]
        n = pdds.nodes[4]
        link = [x for x in nwm.get_plot().itemList() if x.title().text() == u.get_title(l)][0]
        self.assertEqual(link.curveparam._DataSet__icon, u.get_icon(l))
        pass


def drive(test=True):  # pragma: no cover
    if(test):
        unittest.main(verbosity=2)
    else:
        ot = test_network_map()
        ot.setUp()
        ot.test_NetworkMap_scales_to_fit_network_on_creation()
        ot.aw.show()
        sys.exit(ot.app.exec_())

if __name__ == '__main__':  # pragma: no cover
    drive(test=False)
