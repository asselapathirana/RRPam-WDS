from epanettools.epanettools import Link
from epanettools.epanettools import Node


class updates_disabled_temporarily:

    def __init__(self, plot):
        self.plot = plot

    def __enter__(self):
        def nothing():
            pass
        self.__state = self.plot.blockSignals(True)
        # Also set autoreplot to False
        self.__arp = self.plot.autoReplot()
        self.plot.setAutoReplot(False)
        # set updateAxes to False
        self.updateaxes = self.plot.updateAxes
        self.plot.updateAxes = nothing

    def __exit__(self, type, value, traceback):
        # now enable again
        self.plot.blockSignals(self.__state)
        self.plot.SIG_ITEMS_CHANGED.emit(self.plot)  # now manually emit missing signal
        self.plot.setAutoReplot(self.__arp)
        self.plot.autoRefresh()
        # set updateAxes to Proper function and call it too
        self.plot.updateAxes = self.updateaxes
        self.plot.updateAxes()


def get_title(epanet_network_item):
    return _get_type(epanet_network_item)[0]


def get_icon(epanet_network_item):
    return _get_type(epanet_network_item)[1]


def _get_type(epanet_network_item):
    if isinstance(epanet_network_item, Node):
        return "N:" + epanet_network_item.id, 'node.png'
    if isinstance(epanet_network_item, Link):
        return "L:" + epanet_network_item.id, 'link.png'
    if isinstance(epanet_network_item, str):
        if(epanet_network_item == "Risk"):
            return "R:", 'link.png'

    return "None", "curve.png"
