import numpy as np
import pytest

from src.infrastructure.network import Network
from src.infrastructure.network_graph import NetworkGraph
from src.link_layer.checksum import ParityChecksum
from src.link_layer.link_layer import LinkLayer
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config_manager import ConfigManager
from tests.utilities.dummies import DummyPhysicalLayer, CleanChannel
from tests.utilities.utils import make_network_level_hosts


@pytest.fixture
def network_cfg_manager():
    cfg = ConfigManager(top_layer='network')
    return cfg

@pytest.fixture
def clean_channel():
    return CleanChannel()

@pytest.fixture
def empty_graph():
    return NetworkGraph()

@pytest.fixture
def hosts():
    return make_network_level_hosts()

@pytest.fixture
def tile_bits():
    def _make_tile(n):
        return np.tile([0, 1], n)
    return _make_tile

@pytest.fixture
def link_stack():
    cfg = ConfigManager(top_layer='link')
    return ProtocolStack(cfg)

@pytest.fixture
def example_link_layer():
    dummy_physical = DummyPhysicalLayer()
    checksum = ParityChecksum()
    link_layer = LinkLayer(checksum, seq_size=2, payload_size=8, checksum_size=2)
    link_layer.attach_lower(dummy_physical)
    return link_layer

@pytest.fixture
def simple_network(network_cfg_manager):
    return Network(network_cfg_manager)

@pytest.fixture
def linear_network(simple_network, clean_channel):
    host_a = simple_network.create_host(address='192.168.0.1')
    host_b = simple_network.create_host(address='192.168.0.2')
    host_c = simple_network.create_host(address='192.168.0.3')
    simple_network.connect(host_a, host_b, clean_channel)
    simple_network.connect(host_b, host_c, clean_channel)
    simple_network.build_routing_tables()
    return simple_network
