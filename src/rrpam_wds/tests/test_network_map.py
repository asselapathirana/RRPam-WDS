from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging

from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs
from rrpam_wds.gui.dialogs import CurveDialogWithClosable
from rrpam_wds.gui.dialogs import NetworkMap
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


def draw_a_network(aw, network=ex.networks[0], nodes=True, links=True):
    e1 = hs.pdd_service(network, coords=True, adfcalc=True)
    if (nodes):
        nodes = e1.nodes.values()
    else:
        nodes = None
    if (links):
        links = e1.links.values()
    else:
        links = None
    nwm = NetworkMap(name="foo", nodes=nodes, links=links, parent=aw, mainwindow=aw)
    aw.addSubWindow(nwm)
    return e1, nwm


class TC(Test_Parent):

    def test_NetworkMap_is_derived_from_CurveDialogWithClosable(self):
        """NetworkMaph should be derived from CurveDialogWithClosable class"""
        nwm = NetworkMap(name="foo", nodes=None, links=None, parent=self.aw, mainwindow=self.aw)
        self.assertIsInstance(nwm, CurveDialogWithClosable)
        self.aw.addSubWindow(nwm)

    def test_NetworkMap_has_correct_number_of_node_representations(self):
        from guiqwt.curve import CurveItem
        pdds, nwm = draw_a_network(self.aw)
        nodes = pdds.nodes.values()
        curves = [list(zip(x.data().xData(), x.data().yData()))
                  for x in nwm.get_plot().get_items() if(isinstance(x, CurveItem))]
        for node in nodes:
            self.assertIn([(node.x, node.y), (node.x, node.y)], curves)
            # ^ why we represent a node with two identical coordinates?
            # see dialogs.draw_nodes function to know why

    def test_NetworkMap_scales_to_fit_network_on_creation(self):
        pdds, nwm = draw_a_network(self.aw)
        coords = [(n.x, n.y) for n in pdds.nodes.values()]
        xmin = min([x[0] for x in coords])
        xmax = max([x[0] for x in coords])
        ymin = min([x[1] for x in coords])
        ymax = max([x[1] for x in coords])
        logger = logging.getLogger()
        logger.info("values xmin=%s xmax=%s ymin=%s ymax=%s " % (xmin, xmax, ymin, ymax))
        plot = nwm.get_plot()
        _xmin, _xmax = plot.get_axis_limits("bottom")
        _ymin, _ymax = plot.get_axis_limits("left")
        delta = 20.
        self.assertAlmostEqual(xmin - delta, _xmin, delta=delta)
        self.assertAlmostEqual(xmax + delta, _xmax, delta=delta)
        self.assertAlmostEqual(ymin - delta, _ymin, delta=delta)
        self.assertAlmostEqual(ymax + delta, _ymax, delta=delta)

    def test_NetworkMap_has_correct_number_of_link_representations(self):
        for i, network in enumerate(ex.networks[0:1]):  # only one network to make it fast
            if (i == 1):
                continue  # this is Net3.inp - it has a coordinate missing!
            from guiqwt.curve import CurveItem
            pdds, nwm = draw_a_network(self.aw, network=network)
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

        pdds, nwm = draw_a_network(self.aw, network=ex.networks[0])
        # select a link
        l = pdds.links[3]
        pos = [(l.start.x + l.end.x) / 2.0, (l.start.y, l.end.y) / 2.0]
        curve = [x for x in nwm.get_plot().get_items() if x.title().text() == l.id][0]
        plot = curve.plot()
        ax = curve.xAxis()
        ay = curve.yAxis()
        px = plot.transform(ax, pos[0])
        py = plot.transform(ay, pos[1])
        logger = logging.getLogger()
        logger.info(curve.title().text())
        QTest.mouseClick(plot, Qt.RightButton, pos=QPoint(px, py), delay=10.)
        logger = logging.getLogger()
        logger.info(str(plot.get_selected_items()))
        logger = logging.getLogger()
        logger.info((nwm.get_plot().get_selected_items()))
        # this test does not work yet.
        # todo: fix this test to work.

    def test_Network_Map_correctly_reports_selected_links(self):
        import rrpam_wds.gui.utils as u
        pdds, nwm = draw_a_network(self.aw, network=ex.networks[0])
        # select a link
        l = pdds.links[3]
        t = u.get_title(l)
        curve = [x for x in nwm.get_plot().get_items() if x.title().text() == t][0]
        plot = curve.plot()
        curve.select()
        self.assertEqual(len(plot.get_selected_items()), 1)
        self.assertEqual(plot.get_selected_items()[0].title().text(), t)

    def test_nodes_and_their_labels_do_not_have_id_s(self):
        """This is important as not to be confused with similarly named links. We deal only with inks
        in the GUI!."""
        pdds, nwm = draw_a_network(self.aw, network=ex.networks[0], nodes=True, links=False)
        # now this should not have any element with attribute .id_
        n = len([x for x in nwm.get_plot().get_items() if hasattr(x, "id_")])
        self.assertEqual(n, 0)

    def test_links_and_their_labels_do_have_id_s(self):
        pdds, nwm = draw_a_network(self.aw, network=ex.networks[0], nodes=False, links=True)
        n = len([x for x in nwm.get_plot().get_items() if hasattr(x, "id_")])
        self.assertGreaterEqual(n, len(pdds.links.values()) * 2)

    def test_Network_map_item_list_has_correct_icons(self):
        import rrpam_wds.gui.utils as u
        pdds, nwm = draw_a_network(self.aw, network=ex.networks[2])
        # select a link
        l = pdds.links[3]
        pdds.nodes[4]
        link = [x for x in nwm.get_plot().itemList() if x.title().text() == u.get_title(l)][0]
        self.assertEqual(link.curveparam._DataSet__icon, u.get_icon(l))


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
