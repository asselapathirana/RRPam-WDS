import logging
import tempfile

from epanettools.epanettools import EPANetSimulation
from epanettools.epanettools import Link
from epanettools.epanettools import Links
from epanettools.epanettools import Node
from epanettools.epanettools import Nodes

logger = logging.getLogger()


class _Link:
    pass


class _Node:
    pass


class pdd_service(object):

    def __init__(self, epanet_network, diafact=10.0, coords=False, adfcalc=True):
        self.epanet_network = epanet_network
        self.diafact = diafact
        self.adfcalc = adfcalc
        self.open_network(epanet_network)
        if(coords):
            self.read_coordinates(epanet_network)
        self.orig_networkfile = epanet_network

    def read_coordinates(self, epanet_network):
        """Reads the epanet input file and extracts the coorinates of:
            1. nodes
            2. link vertices if any
        """
        with open(epanet_network, 'r') as f:
            l = [x.strip() for x in f.readlines()]
        data = [x for x in l if (x and x != '' and x[0] != ';')]  # drop all empty lines
        st = data.index("[COORDINATES]")
        lines = data[st + 1:-1]

        for line in lines:
            if line[0] + line[-1] == '[]':
                break
            vals = str.split(line)
            self.nodes[vals[0]].x = float(vals[1])
            self.nodes[vals[0]].y = float(vals[2])
        # now check and raise error if a certain node does not have coordinates
        try:
            for i, node in self.nodes.items():
                node.x
                node.y
        except AttributeError as e:

            logger.warn("Exception raised(see below): %e" % e)
            logger.warn(
                "There is an error in your network file, some nodes do not have coordinates. Fix them and retry please.")
            logger.warn("Offending item: %s: Node: %s (%d)" % (epanet_network, node.id, i))

            raise AttributeError(
                "There is an error in your network file, some nodes do not have coordinates. Fix them and retry please.")

        for i, link in self.links.items():
            if (link.start.x == link.end.x):
                link.start.x = link.start.x
                link.end.x = link.end.x

        # now extract vertices (if any)
        st = data.index("[VERTICES]")
        lines = data[st + 1:-1]
        # first add empty list called vertices
        for i, link in self.links.items():
            link.vertices = []
        # now find any vertices and append them
        for line in lines:
            if line[0] + line[-1] == '[]':
                break
            vals = str.split(line)
            self.links[vals[0]].vertices.append((float(vals[1]), float(vals[2])))

    def open_network(self, epanet_network):
        logger.info("Opening network %s" % epanet_network)
        self.es = EPANetSimulation(epanet_network, pdd=True)
        if(self.adfcalc):
            logger.info("Doing ADF calculations")
            self.es.adfcalc(diafact=self.diafact)
        else:
            logger.info("Skipping ADF")
        self._set_static_values()
        # set nodes, links for easy access!

        self.nodes = Nodes()
        self.links = Links()
        logger.info("Mapping nodes and links to new objects")
        for key, value in self.es.network.nodes.items():
            n = _Node()
            n.id = value.id
            # n.x=value.x
            # n.y=value.y
            self.nodes[key] = n

        for key, value in self.es.network.links.items():
            l = _Link()
            l.id = value.id
            l.length = value.length
            l.diameter = value.diameter
            try:
                l.ADF = value.ADF
            except:
                pass
            l.start = self.nodes[value.start.id]
            l.end = self.nodes[value.end.id]
            self.links[key] = l

        # self.nodes = self.es.network.nodes
        # self.links = self.es.network.links

    def _set_static_values(self):
        """ Adds attibutes of length, diameter for easy access."""
        for i, link in self.es.network.links.items():
            d = Link.value_type['EN_DIAMETER']
            l = Link.value_type['EN_LENGTH']
            link.diameter = link.results[d][0]
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

    def _c_and_r(self, vals):
        try:
            r = vals[0]
            results = vals[1]
        except:
            r = vals
            results = None
        if(r != 0):   # pragma: no cover
            raise Exception("epanettools error!")
        return results

    def get_pipe_closed_demand(self, pipeindex, dia_factor):
        import os
        prefix_ = "epanet_" + self._c_and_r(self.es.ENgetlinkid(pipeindex))
        fd, f = tempfile.mkstemp(
            suffix=".inp", prefix=prefix_, dir=tempfile.gettempdir(), text=True)
        os.close(fd)
        d = Link.value_type['EN_DIAMETER']

        ret, diam = self.es.ENgetlinkvalue(pipeindex, d)
        dsmall = diam / float(dia_factor)
        self._c_and_r(self.es.ENsetlinkvalue(pipeindex, d, dsmall))
        self.es.ENsaveinpfile(f)
        self._c_and_r(self.es.ENsetlinkvalue(
            pipeindex, d, diam))  # reset diameter
        self.es = EPANetSimulation(f, pdd=True)
        demand = self.get_total_demand()
        self.es = EPANetSimulation(
            self.orig_networkfile)  # reset original network
        return demand


if __name__ == "__main__":  # pragma no cover
    import os
    from epanettools.examples import simple
    file = os.path.join(os.path.dirname(simple.__file__), 'Net3.inp')
    pd = pdd_service(file)
