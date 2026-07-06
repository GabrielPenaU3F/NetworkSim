import pytest
import numpy as np

from src.infrastructure.network import Network
from src.system_configurations.config import NetworkConfig, IPPacketConfig
from src.system_configurations.config_manager import ConfigManager


@pytest.fixture
def example_network_layer():
    cfg_manager = ConfigManager(top_layer='network',
                                network=NetworkConfig(
                                    packet_cfg=IPPacketConfig(payload_size=8))
                                )
    network = Network(cfg_manager)
    host_a = network.create_host(ip_address='192.168.0.1')
    return host_a._protocol_stack.get_layer('network')


def test_message_reconstructed_after_several_packets(example_network_layer, tile_bits):
    bits = tile_bits(7)
    ip_module = example_network_layer._ip_module
    packets = ip_module.build_packets(bits, '192.168.0.1')

    result = None
    for p in packets:
        serialized = ip_module.serialize_packet(p)
        result = example_network_layer.on_receive(serialized)

    assert np.all(result == bits)

def test_total_serialized_packet_length(example_ip_module, tile_bits):
    bits = tile_bits(7)
    packets = example_ip_module.build_packets(bits, '192.168.0.1')
    serialized = [example_ip_module.serialize_packet(p) for p in packets]

    expected_size = (example_ip_module.address_size * 2
                     + 1
                     + example_ip_module.offset_size
                     + example_ip_module.real_length_size
                     + example_ip_module.packet_payload_size)

    assert len(packets) == 2
    assert len(serialized[0]) == expected_size
    assert len(serialized[1]) == expected_size


class TestARPCircuit:

    pass
    # def test_arp_circuit(self, make_topo_two_hosts_with_switch):
    #     host_a, host_b, switch = make_topo_two_hosts_with_switch('network')
    #     network_layer = host_a._protocol_stack.top_layer
    #     interface_a = host_a.interfaces[0]
    #     network_layer.send_arp_request(target_ip='192.168.0.2', interface=interface_a)