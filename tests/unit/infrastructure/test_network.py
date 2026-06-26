import pytest

from infrastructure.nodes.host import Host
from infrastructure.nodes.switch import Switch
from src.errors import NetworkError, AddressError
from src.infrastructure.network import Network
from src.system_configurations.config_manager import ConfigManager
from system_configurations.config import NetworkConfig


def test_host_without_address_is_allowed_in_link_layer_network():
    cfg = ConfigManager(top_layer='link')
    network = Network(cfg)
    host = network.create_host()
    assert host.address is None

def test_host_without_address_is_allowed_in_physical_layer_network():
    cfg = ConfigManager(top_layer='physical')
    network = Network(cfg)
    host = network.create_host()
    assert host.address is None

def test_cannot_create_host_without_ip_in_network_layer(simple_network):
    with pytest.raises(NetworkError, match='An IP address is required for this network'):
        simple_network.create_host()

def test_cannot_create_two_hosts_with_equal_addresses(simple_network):
    with pytest.raises(AddressError, match='IP address 192.168.0.1 already in use'):
        host_1 = simple_network.create_host(ip_address='192.168.0.1')
        host_2 = simple_network.create_host(ip_address='192.168.0.1')

def test_can_create_host_with_correct_address_format():
    cfg = ConfigManager(top_layer='network', network=NetworkConfig(address_size=24))
    network = Network(cfg)
    host = network.create_host('192.168.0')
    assert host.address == '192.168.0'

def test_network_address_registry_is_updated_when_a_host_is_created(simple_network):
    simple_network.create_host('192.168.0.1')
    simple_network.create_host('192.168.0.2')
    assert '192.168.0.1' in simple_network._address_registry._ip_registry
    assert '192.168.0.2' in simple_network._address_registry._ip_registry

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
    external_host = Host(ConfigManager(top_layer='network'), ip_address='192.168.0.2')
    with pytest.raises(NetworkError, match='Cannot connect nodes that do not belong to this network'):
        simple_network.connect(host_a, external_host, clean_channel)


class TestCreateSwitch:

    def test_create_switch_returns_a_switch_instance(self, simple_network):
        switch = simple_network.create_switch()
        assert isinstance(switch, Switch)

    def test_switch_is_registered_in_graph(self, simple_network):
        switch = simple_network.create_switch()
        assert switch in simple_network.graph.nodes

    def test_switch_has_a_link_module(self, simple_network):
        switch = simple_network.create_switch()
        assert switch.link_module is not None

    def test_switch_link_module_uses_config_checksum(self, simple_network):
        switch = simple_network.create_switch()
        link_cfg = simple_network.cfg_manager.link_layer_cfg
        assert type(switch.link_module.checksum) is type(link_cfg.build_checksum())

    def test_switch_link_module_uses_config_payload_sizes(self, simple_network):
        switch = simple_network.create_switch()
        link_cfg = simple_network.cfg_manager.link_layer_cfg
        assert switch.link_module.min_payload_bits == link_cfg.min_payload_bits
        assert switch.link_module.max_payload_bits == link_cfg.max_payload_bits

    def test_multiple_switches_can_be_created_in_the_same_network(self, simple_network):
        switch_a = simple_network.create_switch()
        switch_b = simple_network.create_switch()
        assert switch_a is not switch_b
        assert simple_network.graph.node_count() == 2

    def test_switch_can_coexist_with_hosts_in_the_same_network(self, simple_network):
        host = simple_network.create_host(ip_address='192.168.0.1')
        switch = simple_network.create_switch()
        assert simple_network.graph.node_count() == 2