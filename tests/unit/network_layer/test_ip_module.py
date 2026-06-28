import numpy as np

from utils import int_to_bits, serialize_ip_address


class TestIPModule:

    def test_packet_is_for_me(self, example_ip_module):
        destination_1 = '192.168.0.1'
        destination_2 = '192.168.0.2'
        assert example_ip_module.packet_is_for_me(destination_1) is True
        assert example_ip_module.packet_is_for_me(destination_2) is False

    def test_contiguous_offsets_are_valid(self, example_ip_module):
        assert example_ip_module.offsets_are_contiguous(0, 8) == True

    def test_non_contiguous_offsets_are_invalid(self, example_ip_module):
        assert example_ip_module.offsets_are_contiguous(0, 16) == False

    def test_reverse_order_offsets_are_invalid(self, example_ip_module):
        assert example_ip_module.offsets_are_contiguous(8, 0) == False

    def test_packet_roundtrip(self, example_ip_module, tile_bits):
        bits = tile_bits(7)
        packets = example_ip_module.build_packets(bits, '192.168.0.1')

        for p in packets:
            serialized = example_ip_module.serialize_packet(p)
            deserialized = example_ip_module.deserialize_packet(serialized)

            assert deserialized.is_last == p.is_last
            assert deserialized.offset == p.offset
            assert deserialized.real_length == p.real_length
            assert np.all(deserialized.payload == p.payload)
            assert deserialized.origin_address == p.origin_address
            assert deserialized.destination_address == p.destination_address

class TestPacketBuilding:

    def test_a_single_packet_is_built(self, example_ip_module):
        packets = example_ip_module.build_packets([0], '192.168.0.1')
        assert len(packets) == 1

    def test_two_packets_are_built(self, example_ip_module, tile_bits):
        bits = tile_bits(8)
        packets = example_ip_module.build_packets(bits, '192.168.0.1')
        assert len(packets) == 2

    def test_single_packet_is_built_with_correct_payload(self, example_ip_module):
        packets = example_ip_module.build_packets([0], '192.168.0.1')
        assert np.all(packets[0].payload == [0])

    def test_two_packets_are_built_with_correct_payload(self, example_ip_module, tile_bits):
        bits = tile_bits(8)
        packets = example_ip_module.build_packets(bits, '192.168.0.1')
        assert np.all(packets[0].payload == tile_bits(4))
        assert np.all(packets[1].payload == tile_bits(4))

    def test_packets_are_built_with_correct_origin_address(self, example_ip_module):
        packets = example_ip_module.build_packets([0], '192.168.0.2')
        assert packets[0].origin_address == '192.168.0.1'

    def test_packets_are_built_with_correct_destination_address(self, example_ip_module):
        packets = example_ip_module.build_packets([0], '192.168.0.2')
        assert packets[0].destination_address == '192.168.0.2'

    def test_is_last_is_1_when_message_fits_a_single_packet(self, example_ip_module):
        packets = example_ip_module.build_packets([0], '192.168.0.1')
        assert packets[0].is_last == 1

    def test_is_last_in_two_packets(self, example_ip_module, tile_bits):
        bits = tile_bits(8)
        packets = example_ip_module.build_packets(bits, '192.168.0.1')
        assert packets[0].is_last == 0
        assert packets[1].is_last == 1

    def test_single_packet_has_zero_offset(self, example_ip_module):
        packets = example_ip_module.build_packets([0], '192.168.0.1')
        assert packets[0].offset == 0

    def test_first_packet_has_zero_offset(self, example_ip_module, tile_bits):
        bits = tile_bits(8) # two packets
        packets = example_ip_module.build_packets(bits, '192.168.0.1')
        assert packets[0].offset == 0

    def test_second_packet_has_correct_offset(self, example_ip_module, tile_bits):
        bits = tile_bits(8) # two packets
        packets = example_ip_module.build_packets(bits, '192.168.0.1')
        assert packets[1].offset == example_ip_module.packet_payload_size

    def test_third_packet_has_correct_offset(self, example_ip_module, tile_bits):
        bits = tile_bits(12)  # 3 packets
        packets = example_ip_module.build_packets(bits, '192.168.0.1')
        assert packets[2].offset == example_ip_module.packet_payload_size * 2


class TestPacketSerialization:

    def test_serialize_packet_origin_address(self, example_ip_module, last_packet):
        serialized = example_ip_module.serialize_packet(last_packet)
        expected_origin = np.array(serialize_ip_address('192.168.0.1'), dtype=np.uint8)
        origin_end = example_ip_module.address_size
        actual_origin = serialized[:origin_end]
        assert np.all(actual_origin == expected_origin)

    def test_serialize_packet_destination_address(self, example_ip_module, last_packet):
        serialized = example_ip_module.serialize_packet(last_packet)
        expected_destination = np.array(serialize_ip_address('192.168.0.2'), dtype=np.uint8)
        origin_end = example_ip_module.address_size
        destination_end = 2 * example_ip_module.address_size
        actual_destination = serialized[origin_end:destination_end]
        assert np.all(actual_destination == expected_destination)

    def test_serialize_packet_is_not_last(self, example_ip_module, packet_to_serialize):
        serialized = example_ip_module.serialize_packet(packet_to_serialize(is_last=0))
        destination_end = 2 * example_ip_module.address_size
        actual_is_last = serialized[destination_end]
        assert actual_is_last == 0

    def test_serialize_packet_is_last(self, example_ip_module, last_packet):
        serialized = example_ip_module.serialize_packet(last_packet)
        destination_end = 2 * example_ip_module.address_size
        actual_is_last = serialized[destination_end]
        assert actual_is_last == 1

    def test_serialize_packet_offset(self, example_ip_module, last_packet):
        expected_offset = np.zeros(8, dtype=np.uint8)
        serialized = example_ip_module.serialize_packet(last_packet)

        offset_start = 2 * example_ip_module.address_size + 1
        offset_size = example_ip_module.offset_size
        actual_offset = serialized[offset_start: offset_start + offset_size]
        assert np.all(actual_offset == expected_offset)

    def test_serialize_packet_real_length(self, example_ip_module, last_packet):
        expected_real_length = int_to_bits(4, 4)
        serialized = example_ip_module.serialize_packet(last_packet)

        offset_start = 2 * example_ip_module.address_size + 1
        offset_end = offset_start + example_ip_module.offset_size
        actual_real_length = serialized[offset_end: offset_end + example_ip_module.real_length_size]
        assert np.all(actual_real_length == expected_real_length)

    def test_serialize_packet_payload(self, example_ip_module, last_packet):
        expected_payload = last_packet.payload
        serialized = example_ip_module.serialize_packet(last_packet)

        payload_start = 2 * example_ip_module.address_size + 1 + example_ip_module.offset_size + example_ip_module.real_length_size
        payload_end = payload_start + example_ip_module.packet_payload_size

        actual_payload = serialized[payload_start: payload_end]
        assert np.all(actual_payload == expected_payload)
        
        
class TestPacketDeserialization:

    def test_deserialize_packet_origin_address(self, example_ip_module, serialized_last_bits):
        deserialized = example_ip_module.deserialize_packet(serialized_last_bits)
        assert deserialized.origin_address == '192.168.0.1'

    def test_deserialize_packet_destination_address(self, example_ip_module, serialized_last_bits):
        deserialized = example_ip_module.deserialize_packet(serialized_last_bits)
        assert deserialized.destination_address == '192.168.0.2'

    def test_deserialize_packet_is_last(self, example_ip_module, serialized_last_bits):
        deserialized = example_ip_module.deserialize_packet(serialized_last_bits)
        assert deserialized.is_last == 1

    def test_deserialize_packet_is_not_last(self, example_ip_module, serialized_bits):
        deserialized = example_ip_module.deserialize_packet(serialized_bits(is_last=0))
        assert deserialized.is_last == 0

    def test_deserialize_packet_offset(self, example_ip_module, serialized_last_bits):
        deserialized = example_ip_module.deserialize_packet(serialized_last_bits)
        assert deserialized.offset == 0

    def test_deserialize_packet_real_length(self, example_ip_module, serialized_last_bits):
        deserialized = example_ip_module.deserialize_packet(serialized_last_bits)
        assert deserialized.real_length == 4

    def test_deserialize_packet_payload(self, example_ip_module, serialized_last_bits):
        deserialized = example_ip_module.deserialize_packet(serialized_last_bits)
        expected_payload = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        assert np.all(deserialized.payload == expected_payload)
