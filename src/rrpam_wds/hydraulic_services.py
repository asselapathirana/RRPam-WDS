from  epanettools.epanettools import EPANetSimulation
from  epanettools.epanettools import Node


class pdd_service(object):
    
    def __init__(self,epanet_network):
        self.open_network(epanet_network)

    def open_network(self, epanet_network):
        self.es=EPANetSimulation(epanet_network)
    
    
    def get_total_demand(self):
        self.es.run()
        total=0.0
        st=self.es.network.tsteps
        for i,node in self.es.network.nodes.items():
            d=Node.value_type["EN_DEMAND"]
            dem=[x*y for x,y in zip(node.results[d],st)]
            total=total+sum(dem)
        return total
    


if __name__ == "__main__":   #pragma no cover
    import os
    from epanettools.examples import simple 
    file = os.path.join(os.path.dirname(simple.__file__),'Net3.inp')
    pd=pdd_service(file)
    print(pd.get_total_demand())
            
        
    
    
    