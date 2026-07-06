from typing import Any

from infrastructure.address_registry import AddressRegistry
from infrastructure.nodes.host import Host
from infrastructure.nodes.switch import Switch
from src.errors import NetworkError
from src.infrastructure.link_factory import LinkFactory
from src.infrastructure.network_graph import NetworkGraph
from src.network_layer.routing_table import RoutingTable


"""
    IP Addresses are formed by parts separated by dots, e.g. 128.192 has 2 parts
    Each part has a fixed size of 8 bits. Thus the cfg parameter address_size 
    determines the number of parts the addresses must have.
"""

class Network:

    def __init__(self, cfg_manager):
        self.cfg_manager = cfg_manager
        ip_address_size = self.cfg_manager.network_layer_cfg.ip_address_size
        self._address_registry = AddressRegistry(ip_address_size)
        self.link_factory = LinkFactory(self._address_registry)
        self.graph = NetworkGraph()
        self.routing = self.routing_algorithm()

    def create_host(self, ip_address=None):
        if ip_address is None and self._requires_ip_address():
            raise NetworkError('An IP address is required for this network')

        if ip_address is not None:
            self._address_registry.register_ip(ip_address)

        host = Host(self.cfg_manager, ip_address=ip_address)
        self.graph.add_node(host)
        return host

    def create_switch(self):
        switch = Switch(self.cfg_manager)
        self.graph.add_node(switch)
        return switch

    def get_topology_graph(self):
        return self.graph

    def connect(self, node_a, node_b, channel):
        if not all(node in self.graph.nodes for node in (node_a, node_b)):
            raise NetworkError('Cannot connect nodes that do not belong to this network')

        self.link_factory.create_link(self.graph, node_a, node_b, channel)

    # TODO: this does nothing now. Will be incorporated on Routers later
    def build_routing_tables(self):
        all_nodes = self.graph.nodes
        for node in all_nodes:
            table = RoutingTable(node)
            first_hops = self.routing.get_first_hops(node)

            for destination, first_hop in first_hops.items():
                edge = self.graph.get_edge_to(node, first_hop)
                iface = edge.get_interface_for(node)
                table.add_entry(destination.ip, iface)

            node.routing_table = table

    def routing_algorithm(self):
        routing_class = self.cfg_manager.network_layer_cfg.routing
        return routing_class(self.graph)

    def get_node(self, ip_address):
        for node in self.graph.nodes:
            if node.ip_address == ip_address:
                return node
        return None

    def _requires_ip_address(self):
        return self.cfg_manager.top_layer not in ('physical', 'link')