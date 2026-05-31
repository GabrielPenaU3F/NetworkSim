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

# def test_packet_is_forwarded_through_intermediate_node(linear_network):
#     linear_network.build_routing_tables()
#     host_a = linear_network.get_node('192.168.0.1')
#     host_c = linear_network.get_node('192.168.0.3')
#     host_a.send("sol", destination_address='192.168.0.3')
#     received = host_c.read()
#
#     assert received == "sol"