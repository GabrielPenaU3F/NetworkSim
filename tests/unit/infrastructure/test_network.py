import pytest

from src.errors import NetworkError
from src.infrastructure.network import Network
from src.infrastructure.nodes import Host
from src.system_configurations.config import NetworkConfig
from src.system_configurations.config_manager import ConfigManager


def test_cannot_create_network_without_network_protocol():
    with pytest.raises(NetworkError, match='Top layer should be at least Network Layer'):
        cfg_manager = ConfigManager(top_layer='link')
        Network(cfg_manager)

def test_network_address_registry_begins_empty(simple_network):
    assert simple_network._address_registry == set()

def test_network_address_registry_is_updated_when_a_host_is_created(simple_network):
    simple_network.create_host('192.168.0.1')
    simple_network.create_host('192.168.0.2')
    assert '192.168.0.1' in simple_network._address_registry
    assert '192.168.0.2' in simple_network._address_registry

def test_cannot_create_two_hosts_with_the_same_address(simple_network):
    simple_network.create_host('192.168.0.1')
    with pytest.raises(NetworkError, match='Address 192.168.0.1 already in use'):
        assert simple_network.create_host('192.168.0.1')

def test_network_should_begin_with_an_empty_graph(simple_network):
    assert simple_network.get_topology_graph().node_count() == 0

def test_network_registers_hosts_in_graph(simple_network):
    simple_network.create_host('192.168.0.1')
    assert simple_network.get_topology_graph().node_count() == 1

def test_connect_creates_interfaces_on_both_hosts(simple_network, clean_channel):
    host_a = simple_network.create_host('192.168.0.1')
    host_b = simple_network.create_host('192.168.0.2')
    simple_network.connect(host_a, host_b, clean_channel)
    assert len(host_a.interfaces) == 1
    assert len(host_b.interfaces) == 1

def test_connect_interfaces_point_to_correct_nodes(simple_network, clean_channel):
    host_a = simple_network.create_host('192.168.0.1')
    host_b = simple_network.create_host('192.168.0.2')
    simple_network.connect(host_a, host_b, clean_channel)
    assert host_a.interfaces[0].node == host_a
    assert host_b.interfaces[0].node == host_b

def test_network_graph_is_updated_when_nodes_are_connected(simple_network, clean_channel):
    host_a =  simple_network.create_host('192.168.0.1')
    host_b = simple_network.create_host('192.168.0.2')
    simple_network.connect(host_a, host_b, clean_channel)
    edge = simple_network.get_topology_graph().get_edge_to(host_a, host_b)
    assert edge.get_other_node(host_a) == host_b
    assert edge.get_other_node(host_b) == host_a

def test_cannot_connect_host_from_another_network(simple_network, clean_channel):
    host_a = simple_network.create_host('192.168.0.1')
    external_host = Host(ConfigManager(top_layer='network'), address='192.168.0.2')
    with pytest.raises(NetworkError, match='Cannot connect nodes that do not belong to this network'):
        simple_network.connect(host_a, external_host, clean_channel)


class TestAddresses:

    def test_network_host_default_address(self, simple_network):
        host = simple_network.create_host()
        assert host.address == '192.168.0.1'

    def test_cannot_create_two_hosts_with_equal_addresses(self, simple_network):
        with pytest.raises(NetworkError, match='Address 192.168.0.1 already in use'):
            host_1 = simple_network.create_host(address='192.168.0.1')
            host_2 = simple_network.create_host(address='192.168.0.1')

    def test_cannot_create_host_with_wrong_address_format(self, simple_network):
        with pytest.raises(NetworkError, match='Addresses must have 4 parts'):
            simple_network.create_host('192.168.0')

    def test_can_create_host_with_correct_address_format(self):
        cfg = ConfigManager(top_layer='network', network=NetworkConfig(address_size=24))
        network = Network(cfg)
        host = network.create_host('192.168.0')
        assert host.address == '192.168.0'
