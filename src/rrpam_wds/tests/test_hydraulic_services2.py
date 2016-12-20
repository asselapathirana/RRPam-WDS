import time
import unittest
import cPickle as pickle

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs
import tempfile

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
        # logger = logging.getLogger()
        print("\ncalculation took %0.2f seconds." % (stop - start))

    def test_pdd_service_network_links_have_diameter_length_and_ADF(self):
        d = 15.
        self.e1 = hs.pdd_service(ex.networks[0], diafact=d)
        # self.e2 = hs.pdd_service(ex.networks[1], diafact=d)
        self.e3 = hs.pdd_service(ex.networks[2], diafact=d)
        self.assertAlmostEqual(self.e3.links[1].length, 100., delta=.0001)
        self.assertAlmostEqual(self.e3.links[1].diameter, 110., delta=.0001)
        self.assertAlmostEqual(self.e3.links[1].ADF, .348, delta=.2)
        self.assertAlmostEqual(self.e3.links['TX'].ADF, .0, delta=.2)
        # logger = logging.getLogger()
        print("\n")
        for i, link in self.e3.links.items():
            # logger = logging.getLogger()
            print("%s\t %0.3f" % (link.id, link.ADF))
            
            
    def test_pdd_service_network_links_are_picklable(self):
        self.e1 = hs.pdd_service(ex.networks[0], coords=True, adfcalc=False)
        import StringIO
        i,name=tempfile.mkstemp(suffix=".rrpamwds_test")
        with open(name,'w+') as output:
            l=self.e1.links[1]
            pickle.dump(l,output)
        with open(name,'r') as inp:
            l_=pickle.load(inp)
        self.assertEqual(l.start.x,l_.start.x)
        
        

if __name__ == '__main__':  # pragma: no cover
    unittest.main(verbosity=2)
