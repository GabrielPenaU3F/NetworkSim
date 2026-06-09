import numpy as np
import pytest

from src.network_layer.network_layer import NetworkLayer
from src.network_layer.packets import IPPacket
from src.utils import serialize_ip_address, int_to_bits
from tests.utilities.dummies import DummyLowerLayer, DummyInterface


@pytest.fixture
def network_layer():
    layer = NetworkLayer('192.168.0.1', address_size=32,
                         offset_size=8, real_length_size=4, packet_payload_size=8)
    # Mock routing callback
    dummy_interface = DummyInterface()
    layer.get_interface_for_address = lambda address: dummy_interface
    return layer

@pytest.fixture
def network_layer_with_dummy_lower(network_layer):
    dummy_lower = DummyLowerLayer()
    network_layer.lower_layer = dummy_lower
    return network_layer, dummy_lower

@pytest.fixture
def last_packet_for_me(tile_bits):
    return IPPacket('127.0.0.1', '192.168.0.1', 1, 0, 8, tile_bits(4))

@pytest.fixture
def nonlast_packet_for_me(tile_bits):
    return IPPacket('127.0.0.1', '192.168.0.1', 0, 0, 8, tile_bits(4))

@pytest.fixture
def nonfull_last_packet_for_me(tile_bits):
    return IPPacket('127.0.0.1', '192.168.0.1', 1, 0, 4, np.concatenate((tile_bits(2), np.zeros(4))))

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

    def test_serialize_packet_real_length(self, network_layer, last_packet):
        expected_real_length = int_to_bits(4, 4)
        serialized = network_layer._serialize_packet(last_packet)

        offset_start = 2 * network_layer.address_size + 1
        offset_end = offset_start + network_layer.offset_size
        actual_real_length = serialized[offset_end: offset_end + network_layer.real_length_size]
        assert np.all(actual_real_length == expected_real_length)

    def test_serialize_packet_payload(self, network_layer, last_packet):
        expected_payload = last_packet.payload
        serialized = network_layer._serialize_packet(last_packet)

        payload_start = 2 * network_layer.address_size + 1 + network_layer.offset_size + network_layer.real_length_size
        payload_end = payload_start + network_layer.packet_payload_size

        actual_payload = serialized[payload_start: payload_end]
        assert np.all(actual_payload == expected_payload)


class TestPacketDeserialization:

    def test_deserialize_packet_origin_address(self, network_layer, serialized_last_bits):
        deserialized = network_layer._deserialize_packet(serialized_last_bits)
        assert deserialized.origin_address == '192.168.0.1'

    def test_deserialize_packet_destination_address(self, network_layer, serialized_last_bits):
        deserialized = network_layer._deserialize_packet(serialized_last_bits)
        assert deserialized.destination_address == '192.168.0.2'

    def test_deserialize_packet_is_last(self, network_layer, serialized_last_bits):
        deserialized = network_layer._deserialize_packet(serialized_last_bits)
        assert deserialized.is_last == 1

    def test_deserialize_packet_is_not_last(self, network_layer, serialized_bits):
        deserialized = network_layer._deserialize_packet(serialized_bits(is_last=0))
        assert deserialized.is_last == 0

    def test_deserialize_packet_offset(self, network_layer, serialized_last_bits):
        deserialized = network_layer._deserialize_packet(serialized_last_bits)
        assert deserialized.offset == 0

    def test_deserialize_packet_real_length(self, network_layer, serialized_last_bits):
        deserialized = network_layer._deserialize_packet(serialized_last_bits)
        assert deserialized.real_length == 4

    def test_deserialize_packet_payload(self, network_layer, serialized_last_bits):
        deserialized = network_layer._deserialize_packet(serialized_last_bits)
        expected_payload = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        assert np.all(deserialized.payload == expected_payload)


class TestMessageComplete:

    def test_empty_buffer_is_not_complete(self, network_layer):
        assert network_layer._message_complete() == False

    def test_single_packet_starting_at_zero_is_complete(self, network_layer):
        network_layer._rx_buffer = {0: np.zeros(8)}
        network_layer._last_received = True
        assert network_layer._message_complete() == True

    def test_single_packet_not_starting_at_zero_is_not_complete(self, network_layer):
        network_layer._rx_buffer = {8: np.zeros(8)}
        network_layer._last_received = True
        assert network_layer._message_complete() == False

    def test_two_contiguous_packets_are_complete(self, network_layer):
        network_layer._rx_buffer = {0: np.zeros(8), 8: np.zeros(8)}
        network_layer._last_received = True
        assert network_layer._message_complete() == True

    def test_two_packets_with_hole_are_not_complete(self, network_layer):
        network_layer._rx_buffer = {0: np.zeros(8), 16: np.zeros(8)}
        network_layer._last_received = True
        assert network_layer._message_complete() == False

    def test_three_contiguous_packets_are_complete(self, network_layer):
        network_layer._rx_buffer = {0: np.zeros(8), 8: np.zeros(8), 16: np.zeros(8)}
        network_layer._last_received = True
        assert network_layer._message_complete() == True

    def test_three_packets_with_missing_middle_are_not_complete(self, network_layer):
        network_layer._rx_buffer = {0: np.zeros(8), 16: np.zeros(8)}
        network_layer._last_received = True
        assert network_layer._message_complete() == False


class TestRebuildMessage:

    def test_single_fragment_is_rebuilt_correctly(self, network_layer):
        payload = np.tile([0, 1], 4)
        network_layer._rx_buffer = {0: (payload, 8)}
        result = network_layer._rebuild_message()
        assert np.all(result == payload)

    def test_two_fragments_are_rebuilt_in_correct_order(self, network_layer):
        payload_1 = np.tile([0, 1], 4)
        payload_2 = np.tile([1, 0], 4)
        network_layer._rx_buffer = {0: (payload_1, 8), 8: (payload_2, 8)}
        result = network_layer._rebuild_message()
        expected = np.concatenate([payload_1, payload_2])
        assert np.all(result == expected)

    def test_fragments_arriving_out_of_order_are_rebuilt_correctly(self, network_layer):
        payload_1 = np.tile([0, 1], 4)
        payload_2 = np.tile([1, 0], 4)
        # buffer desordenado
        network_layer._rx_buffer = {8: (payload_2, 8), 0: (payload_1, 8)}
        result = network_layer._rebuild_message()
        expected = np.concatenate([payload_1, payload_2])
        assert np.all(result == expected)

    def test_buffer_is_cleared_after_rebuild(self, network_layer):
        network_layer._rx_buffer = {0: (np.zeros(8), 0)}
        network_layer._rebuild_message()
        assert network_layer._rx_buffer == {}

    def test_last_received_flag_is_reset_after_rebuild(self, network_layer):
        network_layer._rx_buffer = {0: (np.zeros(8), 0)}
        network_layer._last_received = True
        network_layer._rebuild_message()
        assert network_layer._last_received == False

    def test_payload_is_trimmed_to_real_length(self, network_layer):
        expected_payload = np.tile([1, 0], 2).astype(np.uint8)
        payload_last = np.array([1, 0, 1, 0, 0, 0, 0, 0], dtype=np.uint8)
        network_layer._rx_buffer = {0: (payload_last, 4)}
        assert np.all(network_layer._trim_payload(0) == expected_payload)

    def test_complete_payload_is_not_trimmed(self, network_layer):
        expected_payload = np.tile([1, 0], 4).astype(np.uint8)
        network_layer._rx_buffer = {0: (expected_payload, 8)}
        assert np.all(network_layer._trim_payload(0) == expected_payload)

    def test_last_fragment_is_trimmed_to_real_length(self, network_layer):
        payload_1 = np.tile([0, 1], 4)  # 8 bits reales
        payload_last = np.array([1, 0, 1, 0, 0, 0, 0, 0], dtype=np.uint8)
        network_layer._rx_buffer = {0: (payload_1, 8), 8: (payload_last, 4)}
        result = network_layer._rebuild_message()
        expected = np.concatenate([payload_1, payload_last[:4]])
        assert np.all(result == expected)


class TestNetworkLayerTX:

    def test_transmit_sends_bits_downward(self, network_layer_with_dummy_lower, tile_bits):
        layer, dummy = network_layer_with_dummy_lower
        bits = tile_bits(4)  # 1 packet
        layer.transmit(bits, interface=None, destination_address='192.168.0.2')
        assert dummy.calls == 1

    def test_transmit_sends_one_call_per_packet(self, network_layer_with_dummy_lower, tile_bits):
        layer, dummy = network_layer_with_dummy_lower
        bits = tile_bits(8)  # 2 packets
        layer.transmit(bits, interface=None, destination_address='192.168.0.2')
        assert dummy.calls == 2

    def test_transmit_sends_correct_bit_length(self, network_layer_with_dummy_lower, tile_bits):
        layer, dummy = network_layer_with_dummy_lower
        bits = tile_bits(4)  # 1 packet
        layer.transmit(bits, interface=None, destination_address='192.168.0.2')
        expected_size = layer.address_size * 2 + 1 + layer.offset_size + layer.real_length_size + layer.packet_payload_size
        assert len(dummy.sent_bits[0]) == expected_size


class TestNetworkLayerRX:

    def test_packet_for_this_node_is_accepted(self, network_layer_with_dummy_lower, last_packet_for_me):
        layer, dummy = network_layer_with_dummy_lower
        bits = layer._serialize_packet(last_packet_for_me)
        result = layer.on_receive(bits)
        assert result is not None

    def test_packet_for_another_node_is_forwarded(self, network_layer_with_dummy_lower, last_packet):
        layer, dummy = network_layer_with_dummy_lower

        bits = layer._serialize_packet(last_packet)
        result = layer.on_receive(bits)
        assert result is None
        assert dummy.calls == 1  # Packet was re-sent

    def test_single_packet_message_is_reconstructed(self, network_layer_with_dummy_lower, last_packet_for_me):
        layer, dummy = network_layer_with_dummy_lower
        bits = layer._serialize_packet(last_packet_for_me)
        result = layer.on_receive(bits)
        assert np.all(result == last_packet_for_me.payload)

    def test_incomplete_message_returns_none(self, network_layer_with_dummy_lower, nonlast_packet_for_me):
        layer, dummy = network_layer_with_dummy_lower
        bits = layer._serialize_packet(nonlast_packet_for_me)
        result = layer.on_receive(bits)
        assert result is None

    def test_incomplete_packet_message_is_correctly_reconstructed(self, network_layer_with_dummy_lower,
                                                                  nonfull_last_packet_for_me, tile_bits):
        layer, dummy = network_layer_with_dummy_lower
        bits = layer._serialize_packet(nonfull_last_packet_for_me)
        result = layer.on_receive(bits)
        assert np.all(result == tile_bits(2))

    def test_two_packet_message_is_reconstructed(self, network_layer_with_dummy_lower):
        layer, dummy = network_layer_with_dummy_lower
        payload_1 = np.tile([0, 1], 4)  # 8 bits
        payload_2 = np.tile([1, 0], 4)  # 8 bits
        packet_1 = IPPacket('127.0.0.1', '192.168.0.1', offset=0, is_last=0, real_length=8, payload=payload_1)
        packet_2 = IPPacket('127.0.0.1', '192.168.0.1', offset=8, is_last=1, real_length=8, payload=payload_2)

        bits_1 = layer._serialize_packet(packet_1)
        bits_2 = layer._serialize_packet(packet_2)
        layer.on_receive(bits_1)
        result = layer.on_receive(bits_2)
        expected = np.concatenate([payload_1, payload_2])
        assert np.all(result == expected)

    def test_nonfulL_two_packet_message_is_reconstructed(self, network_layer_with_dummy_lower, tile_bits):
        layer, dummy = network_layer_with_dummy_lower
        payload_1 = tile_bits(4)  # 8 bits
        payload_2 = np.concatenate((np.zeros(4), tile_bits(4))) # 8 bits
        packet_1 = IPPacket('127.0.0.1', '192.168.0.1', offset=0, is_last=0, real_length=8, payload=payload_1)
        packet_2 = IPPacket('127.0.0.1', '192.168.0.1', offset=8, is_last=1, real_length=4, payload=payload_2)

        bits_1 = layer._serialize_packet(packet_1)
        bits_2 = layer._serialize_packet(packet_2)
        layer.on_receive(bits_1)
        result = layer.on_receive(bits_2)
        expected = tile_bits(6)
        assert np.all(result == expected)

    def test_two_packets_reconstructed_in_correct_order(self, network_layer_with_dummy_lower):
        layer, dummy = network_layer_with_dummy_lower
        payload_1 = np.tile([0, 1], 4)
        payload_2 = np.tile([1, 0], 4)
        packet_1 = IPPacket('127.0.0.1', '192.168.0.1', offset=0, is_last=0, real_length=8, payload=payload_1)
        packet_2 = IPPacket('127.0.0.1', '192.168.0.1', offset=8, is_last=1, real_length=8, payload=payload_2)

        # reverse reception order
        bits_2 = layer._serialize_packet(packet_2)
        bits_1 = layer._serialize_packet(packet_1)
        layer.on_receive(bits_2)
        result = layer.on_receive(bits_1)
        expected = np.concatenate([payload_1, payload_2])
        assert np.all(result == expected)

    def test_three_packets_reconstructed_in_correct_order(self, network_layer_with_dummy_lower):
        layer, dummy = network_layer_with_dummy_lower
        payload_1 = np.tile([0, 1], 4)
        payload_2 = np.tile([1, 0], 4)
        payload_3 = np.tile([1, 1], 4)
        packet_1 = IPPacket('127.0.0.1', '192.168.0.1', offset=0, is_last=0, real_length=8, payload=payload_1)
        packet_2 = IPPacket('127.0.0.1', '192.168.0.1', offset=8, is_last=0, real_length=8, payload=payload_2)
        packet_3 = IPPacket('127.0.0.1', '192.168.0.1', offset=16, is_last=1, real_length=8, payload=payload_3)

        # Shuffled reception order
        bits_3 = layer._serialize_packet(packet_3)
        bits_1 = layer._serialize_packet(packet_1)
        bits_2 = layer._serialize_packet(packet_2)
        layer.on_receive(bits_3)
        layer.on_receive(bits_1)
        result = layer.on_receive(bits_2)
        expected = np.concatenate([payload_1, payload_2, payload_3])
        assert np.all(result == expected)


def test_packet_roundtrip(network_layer, tile_bits):
    bits = tile_bits(7)
    packets = network_layer._build_packets(bits, '192.168.0.1')

    for p in packets:
        serialized = network_layer._serialize_packet(p)
        deserialized = network_layer._deserialize_packet(serialized)
        assert deserialized.is_last == p.is_last
        assert deserialized.offset == p.offset
        assert deserialized.real_length == p.real_length
        assert np.all(deserialized.payload == p.payload)
        assert deserialized.origin_address == p.origin_address
        assert deserialized.destination_address == p.destination_address
