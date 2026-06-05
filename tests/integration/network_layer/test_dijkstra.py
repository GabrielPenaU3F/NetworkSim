import pytest


def test_can_select_the_correct_interface_from_routing_table(linear_network):
    a = linear_network.get_node('192.168.0.1')
    b = linear_network.get_node('192.168.0.2')
    edge = a.routing_table.get_interface_to_address('192.168.0.2').edge
    assert edge.get_other_node(a) == b

def test_routing_table_routes_indirect_neighbor_through_correct_interface(linear_network):
    a = linear_network.get_node('192.168.0.1')
    b = linear_network.get_node('192.168.0.2')
    edge = a.routing_table.get_interface_to_address('192.168.0.3').edge
    assert edge.get_other_node(a) == b
