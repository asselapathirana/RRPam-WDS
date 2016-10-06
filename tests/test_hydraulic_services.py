import unittest

from epanettools.epanettools import EPANetSimulation
from mock import patch

import rrpam_wds.examples as ex
from rrpam_wds import hydraulic_services as hs

TOTAL_DEMAND_EX1 = 95045830.
TOTAL_DEMAND_EX2 = 955466043.
TOTAL_DEMAND_EX3 = 965890.

class Testhydraulicservices(unittest.TestCase):

    def setUp(self):
        self.e0 = hs.pdd_service(ex.networks[0])
        self.e1 = hs.pdd_service(ex.networks[1])
        self.e2 = hs.pdd_service(ex.networks[2])

    def tearDown(self):
        pass

    #@pytest.mark.skip(reason="no way of currently testing this")
    # def test_total_demand_returns_sum_of_nodal_demands():
        # assert False

    def test_pdd_service_get_total_demand_calls_run_in_EPANetSimulation(self):
        with patch.object(EPANetSimulation, 'run', autospec=True) as mock_run:
            self.assertFalse(mock_run.called)
            self.e0.get_total_demand()
            self.assertTrue(mock_run.called)

    def test_pdd_service_get_total_demand_will_not_make_initialize_in_EPANetSimulation_called(self):
        with patch.object(EPANetSimulation, 'initialize', autospec=True) as mock_run:
            self.e0.get_total_demand()
            self.assertFalse(mock_run.called)

    def test_pdd_service_object_creation_will_make_initialize_in_EPANetSimulation_called_with_pdd_True(
            self):
        with patch.object(EPANetSimulation, 'initialize', autospec=True) as mock_run:
            pdds = hs.pdd_service(ex.networks[1])
            mock_run.assert_called_once_with(pdds.es, ex.networks[1], pdd=True)

    def test_total_demand_returns_correct_value_ex1(self):
        print(self.e0.es.OriginalInputFileName)
        self.assertAlmostEqual(self.e0.get_total_demand(), TOTAL_DEMAND_EX1, delta=TOTAL_DEMAND_EX1/100.)

    def test_total_demand_returns_correct_value_ex2(self):
        print(self.e1.es.OriginalInputFileName)
        self.assertAlmostEqual(self.e1.get_total_demand(), TOTAL_DEMAND_EX2, delta=TOTAL_DEMAND_EX2/100.)

    def test_total_demand_returns_correct_value_ex3(self):
        print(self.e2.es.OriginalInputFileName)
        self.assertAlmostEqual(self.e2.get_total_demand(), TOTAL_DEMAND_EX3, delta=TOTAL_DEMAND_EX3/100.)
        
    def test_after_closing_a_pipe_pipe_closed_demand_returns_correct_value_ex1_1(self):
        self.assertAlmostEqual(self.e0.get_pipe_closed_demand()-TOTAL_DEMAND_EX1,1000,delta=TOTAL_DEMAND_EX1/100.)


if __name__ == '__main__': # pragma: no cover
    unittest.main(verbosity=2)
