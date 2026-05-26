import pytest

from src.errors import NetworkError
from src.infrastructure.network import Network
from src.infrastructure.nodes import Host
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

def test_network_graph_is_updated_when_nodes_are_connected(simple_network, dummy_channel):
    host_a =  simple_network.create_host('192.168.0.1')
    host_b = simple_network.create_host('192.168.0.2')
    simple_network.connect(host_a, host_b, dummy_channel)
    edge = simple_network.get_topology_graph().get_edge_to(host_a, host_b)
    assert edge.get_other_node(host_a) == host_b
    assert edge.get_other_node(host_b) == host_a

def test_cannot_connect_host_from_another_network(simple_network, dummy_channel):
    host_a = simple_network.create_host('192.168.0.1')
    external_host = Host(ConfigManager(top_layer='network'), address='192.168.0.2')
    with pytest.raises(NetworkError, match='Cannot connect nodes that do not belong to this network'):
        simple_network.connect(host_a, external_host, dummy_channel)
