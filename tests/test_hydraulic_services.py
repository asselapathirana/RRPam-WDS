import pytest

from mock import MagicMock

from  epanettools import epanettools as ep
from  epanettools.epanettools import Node

from rrpam_wds import hydraulic_services as hs

class MockEPANetSimulation(object):
    
    def __init__(self,filename):
        self.filename=filename
        pass
    def run(self):
        self._run=true

class MockNetwork(object):
    
    def __init__(self):
        pass
    

class MockNodes(ep.index_id_type):
    
    pass
    
class MockLinks(ep.index_id_type):
    
    pass    

class Testhydraulicservices:    

    @classmethod
    def setup_class(cls):
        print("Setup")
        mock_EPANetSimulation=MockEPANetSimulation("Foo my file")
        mock_EPANetSimulation.network=MockNetwork()
        mock_EPANetSimulation.network.tsteps=[.5,.8,.3]
        mock_EPANetSimulation.network.nodes=MockNodes()
        mock_EPANetSimulation.network.links=MockLinks()
        d=Node.value_type["EN_DEMAND"]
        NNODES=5
        for i in range(NNODES+1):
            mock_EPANetSimulation.network.nodes[i]=Node(network)
            mock_EPANetSimulation.network.nodes[0].results[]
        mock_EPANetSimulation.network.nodes[0].results[d]=[1,2,3]
        mock_EPANetSimulation.network.nodes[1].results[d]=[2,3,4]
        mock_EPANetSimulation.network.nodes[2].results[d]=[.8,1,2]    
    
        def mock_open_network(self,filename):
            self.es=MockEPANetSimulation(filename)
        
        hs.pdd_service.open_network=mock_open_network
    
    #@pytest.mark.skip(reason="no way of currently testing this")
    #def test_total_demand_returns_sum_of_nodal_demands():
        #assert False 
    
    def test_pdd_service_object_creation_calls_EPANetSimulation_with_filename():
        file="Mynetwork3.inp"  # any name
        pd=hs.pdd_service(file)
        mock_EPANetSimulation.assert_called_once_with(file)
        
    def test_pdd_service_get_total_demand_calls_run_in_EPANetSimulation():
        file="Mynetwork3.inp"  # any name
    
        pd=hs.pdd_service(file)
        assert abs(pd.get_total_demand()-5)==.0001
    
    
    




