import numbers
import time
import unittest

from epanettools.epanettools import EPANetSimulation
from mock import patch

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs

TOTAL_DEMAND_EX1 = 95045830.
TOTAL_DEMAND_EX2 = 945660687.
TOTAL_DEMAND_EX3 = 965890.


class Testhydraulicservices(unittest.TestCase):
    start = 0
    stop = 0

    def setUp(self):
        global start
        start = time.time()

    def tearDown(self):
        global stop
        stop = time.time()
        print("\ncalculation took %0.2f seconds." % (stop - start))
        pass

    def test_pdd_service_network_nodes_have_coordinates(self):
        self.e3 = hs.pdd_service(ex.examples.networks[2], coords=False, adfcalc=False)
        with self.assertRaises(AttributeError):
            self.e3.nodes[1].x
        self.e3 = hs.pdd_service(ex.examples.networks[2], coords=True)
        # Note: we are fudging the coordinates when read in order to walkaround a bug
        # in guiqwt plotting (picking routines) Hence coordinates might have changed a bit
        self.assertAlmostEqual(self.e3.nodes[1].x, -4600., delta=20.)
        self.assertAlmostEqual(self.e3.nodes[1].y, 6600., delta=.0001)
        self.assertAlmostEqual(self.e3.nodes['E2'].x, 600., delta=.001)
        self.assertAlmostEqual(self.e3.nodes['E2'].y, 2200., delta=.001)
        for i, node in self.e3.nodes.items():
            self.assertIsInstance(node.y, numbers.Number)
            self.assertIsInstance(node.x, numbers.Number)
        self.e1 = hs.pdd_service(ex.examples.networks[0], coords=True)
        for i, node in self.e1.nodes.items():
                    self.assertIsInstance(node.y, numbers.Number)
                    self.assertIsInstance(node.x, numbers.Number)
        hs.pdd_service(ex.examples.networks[2])
        with self.assertRaises(AttributeError):
            self.e1 = hs.pdd_service(ex.examples.networks[1], coords=True)

        self.e4 = hs.pdd_service(ex.examples.networks[3], coords=True)
        for i, node in self.e4.nodes.items():
            self.assertIsInstance(node.y, numbers.Number)
            self.assertIsInstance(node.x, numbers.Number)

    def test_pdd_service_network_links_vertices_are_properly_read(self):
        self.e3 = hs.pdd_service(ex.examples.networks[2])
        with self.assertRaises(AttributeError):
            self.e3.links.vertices
        self.e3 = hs.pdd_service(ex.examples.networks[2], coords=True)
        self.assertEqual(self.e3.links['P1'].vertices, [(-6800.00, 6600.00)])
        self.assertEqual(self.e3.links['PUMP1'].vertices, [
                         (-10431.18, 6592.72), (-9800.00, 6600.00)])

        for i, link in self.e3.links.items():
            if(link.id not in ['P1', 'P3', 'P4', 'P5', 'P9', 'P11', 'P13', 'M1', 'M2', 'PUMP1', 'PUMP2']):
                self.assertEqual(len(link.vertices), 0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main(verbosity=2)
