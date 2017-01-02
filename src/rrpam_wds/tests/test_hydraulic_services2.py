import pickle as pickle
import tempfile

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main

TOTAL_DEMAND_EX1 = 95045830.
TOTAL_DEMAND_EX2 = 945660687.
TOTAL_DEMAND_EX3 = 965890.


class TC(Test_Parent):

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
        i, name = tempfile.mkstemp(suffix=".rrpamwds_test")
        with open(name, 'wb+') as output:
            l = self.e1.links[1]
            pickle.dump(l, output)
        with open(name, 'rb') as inp:
            l_ = pickle.load(inp)
        self.assertEqual(l.start.x, l_.start.x)


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
