import types

import pytest

@pytest.fixture
def tableless_network(simple_network, clean_channel):
    host_a = simple_network.create_host(address='192.168.0.1')
    host_b = simple_network.create_host(address='192.168.0.2')
    simple_network.connect(host_a, host_b, clean_channel)
    return simple_network

def test_get_interface_callback_is_empty_before_building_tables(tableless_network):
    network_layer = tableless_network.get_node('192.168.0.1').protocol_stack.get_layer('network')
    assert network_layer.get_interface_for_address is None

def test_get_interface_callback_injected_when_tables_are_built(tableless_network):
    tableless_network.build_routing_tables()
    starting_node = tableless_network.get_node('192.168.0.1')
    network_layer = starting_node.protocol_stack.get_layer('network')

    assert type(network_layer.get_interface_for_address) is types.MethodType
    ending_node = network_layer.get_interface_for_address('192.168.0.2').edge.get_other_node(starting_node)
    assert ending_node.address == '192.168.0.2'
