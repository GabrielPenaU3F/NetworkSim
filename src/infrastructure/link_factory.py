from src.infrastructure.interface import Interface
from src.infrastructure.p2p_link import P2PLink


class LinkFactory:

    @classmethod
    def create_physical_link(cls, node_a, node_b, channel):
        iface_a = Interface(node_a)
        iface_b = Interface(node_b)
        link = P2PLink(iface_a, iface_b, channel)
        iface_a.attach_link(link)
        iface_b.attach_link(link)
        node_a.add_interface(iface_a)
        node_b.add_interface(iface_b)
        return link

    @classmethod
    def create_network_link(cls, graph, node_a, node_b, channel):
        link = LinkFactory.create_physical_link(node_a, node_b, channel)
        graph.add_edge(node_a, node_b, link)
        return link
