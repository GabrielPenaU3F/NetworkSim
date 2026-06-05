import numpy as np
import pytest

from src.network_layer.network_layer import NetworkLayer
from src.utils import serialize_ip_address


@pytest.fixture
def network_layer():
    return NetworkLayer('192.168.0.1', address_size=32, offset_size=8, packet_payload_size=8)

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


class TestPacketSerialization:

    def test_serialize_packet_origin_address(self, network_layer, last_packet):
        serialized = network_layer._serialize_packet(last_packet)
        expected_origin = np.array(serialize_ip_address('192.168.0.1'), dtype=np.uint8)
        origin_end = network_layer.address_size
        actual_origin = serialized[:origin_end]
        assert np.all(actual_origin == expected_origin)

    def test_serialize_packet_destination_address(self, network_layer, last_packet):
        serialized = network_layer._serialize_packet(last_packet)
        expected_destination = np.array(serialize_ip_address('192.168.0.2'), dtype=np.uint8)
        origin_end = network_layer.address_size
        destination_end = 2 * network_layer.address_size
        actual_destination = serialized[origin_end:destination_end]
        assert np.all(actual_destination == expected_destination)

    def test_serialize_packet_is_not_last(self, network_layer, packet_to_serialize):
        serialized = network_layer._serialize_packet(packet_to_serialize(is_last=0))
        destination_end = 2 * network_layer.address_size
        actual_is_last = serialized[destination_end]
        assert actual_is_last == 0

    def test_serialize_packet_is_last(self, network_layer, last_packet):
        serialized = network_layer._serialize_packet(last_packet)
        destination_end = 2 * network_layer.address_size
        actual_is_last = serialized[destination_end]
        assert actual_is_last == 1

    def test_serialize_packet_offset(self, network_layer, last_packet):
        expected_offset = np.zeros(8, dtype=np.uint8)
        serialized = network_layer._serialize_packet(last_packet)

        offset_start = 2 * network_layer.address_size + 1
        offset_size = network_layer.offset_size
        actual_offset = serialized[offset_start: offset_start + offset_size]
        assert np.all(actual_offset == expected_offset)

    def test_serialize_packet_payload(self, network_layer, last_packet):
        expected_payload = last_packet.payload
        serialized = network_layer._serialize_packet(last_packet)

        payload_start = 2 * network_layer.address_size + 1 + network_layer.offset_size
        payload_end = payload_start + network_layer.packet_payload_size

        actual_payload = serialized[payload_start: payload_end]
        assert np.all(actual_payload == expected_payload)



# class TestPacketDeserialization:
#
#     def test_deserialize_frame_seq(self, example_link_layer, serialized_bits):
#         deserialized = example_link_layer._deserialize_frame(serialized_bits())
#         assert deserialized.seq == 0
#
#     def test_deserialize_frame_is_last(self, example_link_layer, serialized_bits):
#         deserialized = example_link_layer._deserialize_frame(serialized_bits(is_last=1))
#         assert deserialized.is_last == 1
#
#     def test_deserialize_frame_is_not_last(self, example_link_layer, serialized_bits):
#         deserialized = example_link_layer._deserialize_frame(serialized_bits(is_last=0))
#         assert deserialized.is_last == 0
#
#     def test_deserialize_frame_is_ack(self, example_link_layer, serialized_bits):
#         deserialized = example_link_layer._deserialize_frame(serialized_bits(is_ack=1))
#         assert deserialized.is_ack == 1
#
#     def test_deserialize_frame_is_not_ack(self, example_link_layer, serialized_bits):
#         deserialized = example_link_layer._deserialize_frame(serialized_bits(is_ack=0))
#         assert deserialized.is_ack == 0
#
#     def test_deserialize_frame_real_length(self, example_link_layer, serialized_bits):
#         deserialized = example_link_layer._deserialize_frame(serialized_bits())
#         assert deserialized.real_length == 4
#
#     def test_deserialize_frame_payload(self, example_link_layer, serialized_bits):
#         deserialized = example_link_layer._deserialize_frame(serialized_bits())
#         expected_payload = np.array([0, 1, 0, 1], dtype=np.uint8)
#         assert np.all(deserialized.payload == expected_payload)