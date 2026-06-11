import types

import pytest
import numpy as np

from src.infrastructure.network import Network
from src.system_configurations.config import NetworkConfig, PacketConfig
from src.system_configurations.config_manager import ConfigManager


@pytest.fixture
def example_network_layer():
    cfg_manager = ConfigManager(top_layer='network',
                                network=NetworkConfig(
                                    packet_cfg=PacketConfig(payload_size=8))
                                )
    network = Network(cfg_manager)
    host_a = network.create_host(address='192.168.0.1')
    return host_a.protocol_stack.get_layer('network')

@pytest.fixture
def tableless_network(simple_network, clean_channel):
    host_a = simple_network.create_host(address='192.168.0.1')
    host_b = simple_network.create_host(address='192.168.0.2')
    simple_network.connect(host_a, host_b, clean_channel)
    return simple_network


def test_get_interface_callback_is_a_void_function_before_building_tables(tableless_network):
    network_layer = tableless_network.get_node('192.168.0.1').protocol_stack.get_layer('network')
    assert network_layer.get_interface_for_address('something') is None

def test_get_interface_callback_injected_when_tables_are_built(tableless_network):
    tableless_network.build_routing_tables()
    starting_node = tableless_network.get_node('192.168.0.1')
    network_layer = starting_node.protocol_stack.get_layer('network')

    assert type(network_layer.get_interface_for_address) is types.MethodType
    ending_node = network_layer.get_interface_for_address('192.168.0.2').edge.get_other_node(starting_node)
    assert ending_node.address == '192.168.0.2'

def test_message_reconstructed_after_several_packets(example_network_layer, tile_bits):
    bits = tile_bits(7)
    packets = example_network_layer._build_packets(bits, '192.168.0.1')

    result = None
    for p in packets:
        serialized = example_network_layer._serialize_packet(p)
        result = example_network_layer.on_receive(serialized)

    assert np.all(result == bits)

def test_total_serialized_packet_length(example_network_layer, tile_bits):
    bits = tile_bits(7)
    packets = example_network_layer._build_packets(bits, '192.168.0.1')
    serialized = [example_network_layer._serialize_packet(p) for p in packets]

    expected_size = (example_network_layer.address_size * 2
                    + 1
                    + example_network_layer.offset_size
                    + example_network_layer.real_length_size
                    + example_network_layer.packet_payload_size)

    assert len(packets) == 2
    assert len(serialized[0]) == expected_size
    assert len(serialized[1]) == expected_size
