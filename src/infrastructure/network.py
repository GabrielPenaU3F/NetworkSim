from src.errors import NetworkError
from src.infrastructure.link_factory import LinkFactory
from src.infrastructure.network_graph import NetworkGraph
from src.infrastructure.nodes import Host
from src.network_layer.routing_table import RoutingTable


"""
    IP Addresses are formed by parts separated by dots, e.g. 128.192 has 2 parts
    Each part has a fixed size of 8 bits. Thus the cfg parameter address_size 
    determines the number of parts the addresses must have.
"""

class Network:

    _address_registry = None
    cfg_manager = None

    def __init__(self, cfg_manager):
        self._validate_config(cfg_manager)
        self.cfg_manager = cfg_manager
        self._address_registry = set()
        self.graph = NetworkGraph()
        self.routing = self.routing_algorithm()

    def create_host(self, address='192.168.0.1'):
        self._validate_address(address)

        host = Host(self.cfg_manager, address=address)
        self._address_registry.add(address)
        self.graph.add_node(host)
        return host

    def _validate_address(self, address):
        expected_parts = self.cfg_manager.network_layer_cfg.address_size // 8
        actual_parts = len(address.split('.'))
        if actual_parts != expected_parts:
            raise NetworkError(f'Addresses must have {expected_parts} parts, got {actual_parts}')
        if address in self._address_registry:
            raise NetworkError(f'Address {address} already in use')

    def _validate_config(self, cfg_manager):
        top_layer = cfg_manager.top_layer
        if top_layer in ['physical', 'link']:
            raise NetworkError('Top layer should be at least Network Layer')

    def get_topology_graph(self):
        return self.graph

    def connect(self, node_a, node_b, channel):
        if not all(node.address in self._address_registry for node in (node_a, node_b)):
            raise NetworkError('Cannot connect nodes that do not belong to this network')
        LinkFactory.create_network_link(self.graph, node_a, node_b, channel)

    def build_routing_tables(self):
        all_nodes = self.graph.nodes
        for node in all_nodes:
            table = RoutingTable(node)
            first_hops = self.routing.get_first_hops(node)

            for destination, first_hop in first_hops.items():
                edge = self.graph.get_edge_to(node, first_hop)
                iface = edge.get_interface_for(node)
                table.add_entry(destination.address, iface)

            node.routing_table = table

            network_layer = node.protocol_stack.get_layer('network')
            if network_layer is not None:
                network_layer.set_routing_callback(node.routing_table.get_interface_to_address)

    def routing_algorithm(self):
        routing_class = self.cfg_manager.network_layer_cfg.routing
        return routing_class(self.graph)

    def get_node(self, address):
        for node in self.graph.nodes:
            if node.address == address:
                return node
        return None