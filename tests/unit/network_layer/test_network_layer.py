import numpy as np
import pytest

from src.network_layer.network_layer import NetworkLayer


@pytest.fixture
def network_layer():
    return NetworkLayer('192.168.0.1', address_size=32, packet_payload_size=8)

class TestPacketBuilding:

    def test_a_single_packet_is_built(self, network_layer):
        packets = network_layer._build_packets([0], '192.168.0.1')
        assert len(packets) == 1

    def test_two_packets_are_built(self, network_layer, tile_bits):
        bits = tile_bits(8)
        packets = network_layer._build_packets(bits, '192.168.0.1')
        assert len(packets) == 2

    def test_single_packet_is_built_with_correct_payload(self, network_layer):
        packets = network_layer._build_packets([0], '192.168.0.1')
        assert np.all(packets[0].payload == [0])

    def test_two_packets_are_built_with_correct_payload(self, network_layer, tile_bits):
        bits = tile_bits(8)
        packets = network_layer._build_packets(bits, '192.168.0.1')
        assert np.all(packets[0].payload == tile_bits(4))
        assert np.all(packets[1].payload == tile_bits(4))

    def test_packets_are_built_with_correct_origin_address(self, network_layer):
        packets = network_layer._build_packets([0], '192.168.0.2')
        assert packets[0].origin_address == '192.168.0.1'

    def test_packets_are_built_with_correct_destination_address(self, network_layer):
        packets = network_layer._build_packets([0], '192.168.0.2')
        assert packets[0].destination_address == '192.168.0.2'

    def test_is_last_is_1_when_message_fits_a_single_packet(self, network_layer):
        packets = network_layer._build_packets([0], '192.168.0.1')
        assert packets[0].is_last == 1

    def test_is_last_in_two_packets(self, network_layer, tile_bits):
        bits = tile_bits(8)
        packets = network_layer._build_packets(bits, '192.168.0.1')
        assert packets[0].is_last == 0
        assert packets[1].is_last == 1

    def test_single_packet_has_zero_offset(self, network_layer):
        packets = network_layer._build_packets([0], '192.168.0.1')
        assert packets[0].offset == 0

    def test_first_packet_has_zero_offset(self, network_layer, tile_bits):
        bits = tile_bits(8) # two packets
        packets = network_layer._build_packets(bits, '192.168.0.1')
        assert packets[0].offset == 0

    def test_second_packet_has_correct_offset(self, network_layer, tile_bits):
        bits = tile_bits(8) # two packets
        packets = network_layer._build_packets(bits, '192.168.0.1')
        assert packets[1].offset == network_layer.packet_payload_size

    def test_third_packet_has_correct_offset(self, network_layer, tile_bits):
        bits = tile_bits(12)  # 3 packets
        packets = network_layer._build_packets(bits, '192.168.0.1')
        assert packets[2].offset == network_layer.packet_payload_size * 2
