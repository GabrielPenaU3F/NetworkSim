import pytest

from src.infrastructure.network import Network
from src.system_configurations.config_manager import ConfigManager
from tests.utilities.dummies import CleanChannel

def test_can_select_the_correct_interface_from_routing_table(linear_network):
    a = linear_network.get_node('192.168.0.1')
    b = linear_network.get_node('192.168.0.2')
    edge = a.routing_table.get_interface(b).edge
    assert edge.get_other_node(a) == b

def test_routing_table_routes_indirect_neighbor_through_correct_interface(linear_network):
    a = linear_network.get_node('192.168.0.1')
    b = linear_network.get_node('192.168.0.2')
    c = linear_network.get_node('192.168.0.3')
    edge = a.routing_table.get_interface(b).edge
    assert edge.get_other_node(a) == b

# def test_packet_is_forwarded_through_intermediate_node():
#     network = Network(ConfigManager(top_layer='network'))
#
#     host_a = network.create_host(address='192.168.0.1')
#     host_b = network.create_host(address='192.168.0.2')
#     host_c = network.create_host(address='192.168.0.3')
#
#     channel = BinarySymmetricChannel(error_prob=0)
#
#     network.connect(host_a, host_b, channel)
#     network.connect(host_b, host_c, channel)
#
#     network.build_routing_tables()
#
#     host_a.send("sol", destination='192.168.0.3')
#     received = host_c.read()
#
#     assert received == "sol"