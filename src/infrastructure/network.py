from src.errors import NetworkError
from src.infrastructure.link_factory import LinkFactory
from src.infrastructure.network_graph import NetworkGraph
from src.infrastructure.nodes import Host


class Network:

    _address_registry = None
    cfg_manager = None

    def __init__(self, cfg_manager):
        self._validate_config(cfg_manager)
        self.cfg_manager = cfg_manager
        self._address_registry = set()
        self.graph = NetworkGraph()

    def create_host(self, address='192.168.0.1'):

        if address in self._address_registry:
            raise NetworkError(f'Address {address} already in use')

        host = Host(self.cfg_manager, address=address)
        self._address_registry.add(address)
        self.graph.add_node(host)
        return host

    def _validate_config(self, cfg_manager):
        top_layer = cfg_manager.get_protocol_stack_config().top_layer
        if top_layer in ['physical', 'link']:
            raise NetworkError('Top layer should be at least Network Layer')

    def get_topology_graph(self):
        return self.graph

    def connect(self, node_a, node_b, channel):
        if not all(node.get_address() in self._address_registry for node in (node_a, node_b)):
            raise NetworkError('Cannot connect nodes that do not belong to this network')
        LinkFactory.create_network_link(self.graph, node_a, node_b, channel)
