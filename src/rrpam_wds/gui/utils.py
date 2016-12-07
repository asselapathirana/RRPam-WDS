from epanettools.epanettools import Link
from epanettools.epanettools import Node


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

    return "None", None
