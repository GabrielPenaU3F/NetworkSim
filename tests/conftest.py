from unittest.mock import Mock

import numpy as np
import pytest

from network_layer.network_layer import NetworkLayer
from network_layer.network_modules.ip_module import IPModule
from src.infrastructure.network import Network
from src.infrastructure.network_graph import NetworkGraph
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config_manager import ConfigManager
from tests.utilities.dummies import DummyLowerLayer, CleanChannel, DummyNode, DummyInterface
from infrastructure.checksum import ParityChecksum
from transport_layer.old_link_layer import OldLinkLayer

@pytest.fixture
def link_cfg_manager():
    cfg = ConfigManager(top_layer='link')
    return cfg

@pytest.fixture
def network_cfg_manager():
    cfg = ConfigManager(top_layer='network')
    return cfg

@pytest.fixture
def clean_channel():
    return CleanChannel()

@pytest.fixture
def dummy_interface():
    return DummyInterface()

@pytest.fixture
def empty_graph():
    return NetworkGraph()

@pytest.fixture
def three_dummy_hosts():
    a = DummyNode(ip_address='192.168.0.1')
    b = DummyNode(ip_address='192.168.0.2')
    c = DummyNode(ip_address='192.168.0.3')
    return a, b, c

@pytest.fixture
def tile_bits():
    def _make_tile(n):
        return np.tile([0, 1], n).astype(np.uint8)
    return _make_tile

@pytest.fixture
def link_stack():
    cfg = ConfigManager(top_layer='link')
    return ProtocolStack(cfg)

@pytest.fixture
def example_link_layer():
    dummy_physical = DummyLowerLayer()
    checksum = ParityChecksum()
    link_layer = OldLinkLayer(checksum, seq_size=2, payload_size=8, checksum_size=2)
    link_layer.attach_lower(dummy_physical)
    return link_layer

@pytest.fixture
def simple_network(network_cfg_manager):
    return Network(network_cfg_manager)

@pytest.fixture
def linear_network(simple_network, clean_channel):
    host_a = simple_network.create_host(ip_address='192.168.0.1')
    host_b = simple_network.create_host(ip_address='192.168.0.2')
    host_c = simple_network.create_host(ip_address='192.168.0.3')
    simple_network.connect(host_a, host_b, clean_channel)
    simple_network.connect(host_b, host_c, clean_channel)
    return simple_network

@pytest.fixture
def mock_graph():
    graph = Mock()
    graph.add_edge.return_value = Mock()
    return graph

@pytest.fixture
def example_ip_module():
    return IPModule(
        ip='192.168.0.1',
        address_size=32,
        offset_size=8,
        real_length_size=4,
        packet_payload_size=8
    )

@pytest.fixture
def example_network_layer():
    layer = NetworkLayer('192.168.0.1', address_size=32,
                         offset_size=8, real_length_size=4, packet_payload_size=8)
    return layer

@pytest.fixture
def network_layer_with_dummy_lower(example_network_layer):
    dummy_lower = DummyLowerLayer()
    example_network_layer.lower_layer = dummy_lower
    return example_network_layer, dummy_lower