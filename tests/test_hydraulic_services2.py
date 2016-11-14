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
    start=0
    stop=0

    def setUp(self):
        global start
        start=time.time()
        d=15.
        self.e1 = hs.pdd_service(ex.networks[0], diafact=d)
        #self.e2 = hs.pdd_service(ex.networks[1], diafact=d)
        self.e3 = hs.pdd_service(ex.networks[2], diafact=d)
        

    def tearDown(self):
        global stop
        stop=time.time()
        print("\ncalculation took %0.2f seconds." % (stop-start))
        pass


    def test_pdd_service_network_links_have_diameter_length_and_ADF(self):
        self.assertAlmostEqual(self.e3.links[1].length,100.,delta=.0001)
        self.assertAlmostEqual(self.e3.links[1].diameter,110.,delta=.0001)
        self.assertAlmostEqual(self.e3.links[1].ADF,.348,delta=.2)
        self.assertAlmostEqual(self.e3.links['TX'].ADF,.0,delta=.2)
        print("\n")
        for i,link in self.e3.links.items():
            print ("%s\t %0.3f" %(link.id,link.ADF))

if __name__ == '__main__':  # pragma: no cover
    unittest.main(verbosity=2)
