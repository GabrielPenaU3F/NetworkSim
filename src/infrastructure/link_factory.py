from src.infrastructure.interface import Interface
from src.infrastructure.p2p_link import P2PLink


class LinkFactory:

    def __init__(self, address_registry):
        self.address_registry = address_registry

    def create_link(self, graph, node_a, node_b, channel):
        link, iface_a, iface_b = self._build_link(node_a, node_b, channel)
        edge = graph.add_edge(node_a, node_b, link)
        node_a.add_interface(iface_a, edge)
        node_b.add_interface(iface_b, edge)
        return link

    def _build_link(self, node_a, node_b, channel):
        iface_a = Interface(node_a)
        iface_b = Interface(node_b)
        iface_a.mac_address = self.address_registry.generate_mac()
        iface_b.mac_address = self.address_registry.generate_mac()

        link = P2PLink(iface_a, iface_b, channel)
        iface_a.attach_link(link)
        iface_b.attach_link(link)
        return link, iface_a, iface_b
    