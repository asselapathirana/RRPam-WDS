import tempfile
from epanettools.epanettools import EPANetSimulation
from epanettools.epanettools import Node, Link



class pdd_service(object):

    def __init__(self, epanet_network,diafact=10.0):
        self.diafact=diafact        
        self.open_network(epanet_network)
        self.orig_networkfile=epanet_network

    def open_network(self, epanet_network):
        self.es = EPANetSimulation(epanet_network, pdd=True)
        self.es.adfcalc(diafact=self.diafact)
        self._set_static_values()
        # set nodes, links for easy access!
        self.nodes=self.es.network.nodes
        self.links=self.es.network.links
        
    def _set_static_values(self):
        """ Adds attibutes of length, diameter for easy access."""
        for i,link in self.es.network.links.items():
            d = Link.value_type['EN_DIAMETER']
            l = Link.value_type['EN_LENGTH']
            link.diameter=link.results[d][0]
            link.length = link.results[l][0]

            

    def get_total_demand(self):
        self.es.run()
        total = 0.0
        st = self.es.network.tsteps
        j = Node.node_types['JUNCTION']
        for (i, node) in [(i, x) for i, x in self.es.network.nodes.items() if x.node_type == j]:
            d = Node.value_type["EN_DEMAND"]
            dem = [x * y for x, y in zip(node.results[d], st)]
            total = total + sum(dem)
        return total    
    
    def _c_and_r(self,vals):
        try:
            r=vals[0]
            results=vals[1]
        except: 
            r=vals
            results=None
        if(r != 0):
            raise Exception("epanettools error!")        
        return results

    def get_pipe_closed_demand(self, pipeindex,dia_factor):
        import os
        prefix_="epanet_"+self.es.ENgetlinkid(pipeindex)[1]
        fd, f = tempfile.mkstemp(
            suffix=".inp", prefix=prefix_, dir=tempfile.gettempdir(), text=True)
        os.close(fd)
        d = Link.value_type['EN_DIAMETER']

        ret, diam = self.es.ENgetlinkvalue(pipeindex, d)
        dsmall=diam/float(dia_factor)
        self._c_and_r(self.es.ENsetlinkvalue(pipeindex, d, dsmall))
        self.es.ENsaveinpfile(f)
        self._c_and_r(self.es.ENsetlinkvalue(pipeindex, d, diam)) # reset diameter
        self.es = EPANetSimulation(f,pdd=True)
        demand=self.get_total_demand()
        self.es=EPANetSimulation(self.orig_networkfile) # reset original network
        return demand


if __name__ == "__main__":  # pragma no cover
    import os
    from epanettools.examples import simple
    file = os.path.join(os.path.dirname(simple.__file__), 'Net3.inp')
    pd = pdd_service(file)
    total=pd.get_total_demand()
    for i in range(6,120):
        print ("%4.2f" % (pd.get_pipe_closed_demand(i,100.)/total))
