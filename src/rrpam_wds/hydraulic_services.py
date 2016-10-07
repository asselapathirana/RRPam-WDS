import tempfile, os
from epanettools.epanettools import EPANetSimulation
from epanettools.epanettools import Node, Link

def _get_total_demand(ensim):
    ensim.run()
    total = 0.0
    st = ensim.network.tsteps
    j = Node.node_types['JUNCTION']
    for (i, node) in [(i, x) for i, x in ensim.network.nodes.items() if x.node_type == j]:
        d = Node.value_type["EN_DEMAND"]
        dem = [x * y for x, y in zip(node.results[d], st)]
        total = total + sum(dem)
    return total


class pdd_service(object):

    def __init__(self, epanet_network):
        self.open_network(epanet_network)

    def open_network(self, epanet_network):
        self.es = EPANetSimulation(epanet_network, pdd=True)

    def get_total_demand(self):
        return _get_total_demand(self.es)
    

   
    def get_pipe_closed_demand(self,pipeindex):
        fd,f=tempfile.mkstemp(suffix=".inp", prefix="epanet_", dir=tempfile.gettempdir(), text=True)
        os.close(fd)
        d=Link.value_type['EN_DIAMETER']
        if (pipeindex > 0):
            ret,dsmall=self.es.ENgetlinkvalue(pipeindex,d)
            r=self.es.ENsetlinkvalue(pipeindex,d,dsmall)
        self.es.ENsaveinpfile(f)
        e2=EPANetSimulation(f)
        return _get_total_demand(e2)
    


if __name__ == "__main__":  # pragma no cover
    import os
    from epanettools.examples import simple
    file = os.path.join(os.path.dirname(simple.__file__), 'Net3.inp')
    pd = pdd_service(file)
    print(pd.get_total_demand())
