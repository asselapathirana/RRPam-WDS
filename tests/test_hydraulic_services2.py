import unittest

from epanettools.epanettools import EPANetSimulation
from mock import patch

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs

TOTAL_DEMAND_EX1 = 95045830.
TOTAL_DEMAND_EX2 = 945660687.
TOTAL_DEMAND_EX3 = 965890.


class Testhydraulicservices(unittest.TestCase):

    def setUp(self):
        self.e1 = hs.pdd_service(ex.networks[0])
        self.e2 = hs.pdd_service(ex.networks[1])
        self.e3 = hs.pdd_service(ex.networks[2], diafact=4.)


    def tearDown(self):
        pass


    def test_pdd_service_network_links_have_diameter_length_and_ADF(self):
        self.assertAlmostEqual(self.e3.links[1].length,100.,delta=.0001)
        self.assertAlmostEqual(self.e3.links[1].diameter,110.,delta=.0001)
        self.assertAlmostEqual(self.e3.links[1].ADF,.478,delta=.01)
        

if __name__ == '__main__':  # pragma: no cover
    unittest.main(verbosity=2)
