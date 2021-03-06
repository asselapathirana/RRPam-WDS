import numbers

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main

TOTAL_DEMAND_EX1 = 95045830.
TOTAL_DEMAND_EX2 = 945660687.
TOTAL_DEMAND_EX3 = 965890.


class TC(Test_Parent):

    def test_pdd_service_network_nodes_have_coordinates1(self):
        self.e3 = hs.pdd_service(ex.examples.networks[2], coords=False, adfcalc=False)
        with self.assertRaises(AttributeError):
            self.e3.nodes[1].x
        self.e3 = hs.pdd_service(ex.examples.networks[2], coords=True)
        self.assertAlmostEqual(self.e3.nodes[1].x, -4600., delta=0.0001)
        self.assertAlmostEqual(self.e3.nodes[1].y, 6600., delta=.0001)
        self.assertAlmostEqual(self.e3.nodes['E2'].x, 600., delta=.001)
        self.assertAlmostEqual(self.e3.nodes['E2'].y, 2200., delta=.001)
        for i, node in self.e3.nodes.items():
            self.assertIsInstance(node.y, numbers.Number)
            self.assertIsInstance(node.x, numbers.Number)

    def test_pdd_service_network_nodes_have_coordinates2(self):
        self.e1 = hs.pdd_service(ex.examples.networks[2], coords=True, adfcalc=False)
        # with self.assertRaises(AttributeError):
        #    self.e1 = hs.pdd_service(ex.examples.networks[1], coords=True)
        for i, node in self.e1.nodes.items():
            self.assertIsInstance(node.y, numbers.Number)
            self.assertIsInstance(node.x, numbers.Number)

    def test_pdd_service_network_nodes_have_coordinates3(self):
        self.e4 = hs.pdd_service(ex.examples.networks[3], coords=True, adfcalc=False)
        for i, node in self.e4.nodes.items():
            self.assertIsInstance(node.y, numbers.Number)
            self.assertIsInstance(node.x, numbers.Number)

    def test_pdd_service_network_links_have_nodes_at_ends(self):
        self.e1 = hs.pdd_service(ex.examples.networks[0], coords=True)
        nodes = list(self.e1.nodes.values())
        for i, link in self.e1.links.items():
            self.assertIn(link.start, nodes)

    def test_pdd_service_network_links_vertices_are_properly_read(self):
        self.e3 = hs.pdd_service(ex.examples.networks[2])
        with self.assertRaises(AttributeError):
            self.e3.links.vertices
        self.e3 = hs.pdd_service(ex.examples.networks[2], coords=True, adfcalc=False)
        self.assertEqual(self.e3.links['P1'].vertices, [(-6800.00, 6600.00)])
        self.assertEqual(self.e3.links['PUMP1'].vertices, [
                         (-10431.18, 6592.72), (-9800.00, 6600.00)])

        for i, link in self.e3.links.items():
            if(link.id not in ['P1', 'P3', 'P4', 'P5', 'P9', 'P11', 'P13', 'M1', 'M2', 'PUMP1', 'PUMP2']):
                self.assertEqual(len(link.vertices), 0)

    def test_pdd_service_has_units(self):
        self.e0 = hs.pdd_service(ex.examples.networks[0])
        self.e1 = hs.pdd_service(ex.examples.networks[1])
        self.e2 = hs.pdd_service(ex.examples.networks[2])
        self.e3 = hs.pdd_service(ex.examples.networks[3])
        self.assertEqual(self.e0.units, 'GPM')
        self.assertEqual(self.e1.units, 'GPM')
        self.assertEqual(self.e2.units, 'LPS')
        self.assertEqual(self.e3.units, 'GPM')


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
