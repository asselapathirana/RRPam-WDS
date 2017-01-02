import logging

from epanettools.epanettools import Link
from epanettools.epanettools import Node


class updates_disabled_temporarily:

    def __init__(self, plot):
        self.plot = plot
        self.set1 = False
        self.set2 = False
        self.set3 = False
        self.logger = logging.getLogger()

    def __enter__(self):

        def nothing():
            pass
        if (hasattr(self.plot, "SIG_ITEMS_CHANGED")):
            self.__state = self.plot.blockSignals(True)
            self.set1 = True
        # Also set autoreplot to False
        if (hasattr(self.plot, "autoReplot")):
            self.__arp = self.plot.autoReplot()
            self.plot.setAutoReplot(False)
            self.set2 = True
        # set updateAxes to False
        if (hasattr(self.plot, "updateAxes")):
            self.updateaxes = self.plot.updateAxes
            self.plot.updateAxes = nothing
            self.set3 = True

    def __exit__(self, type, value, traceback):
        # now enable again
        if (self.set1):
            st = self.plot.blockSignals(self.__state)
            self.plot.SIG_ITEMS_CHANGED.emit(self.plot)  # now manually emit missing signal
            self.logger.info("blockSignals %s --> %s" % (st, self.__state))
        if (self.set2):
            self.plot.setAutoReplot(self.__arp)
            self.logger.info("setAutoReplot %s --> %s (& replotting)" % (self.__arp, True))
            self.plot.replot()
        # set updateAxes to Proper function and call it too
        if (self.set3):
            self.plot.updateAxes = self.updateaxes
            self.logger.info("updateAxes %s --> %s (& updating)" % ("nothing", self.updateaxes))
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
