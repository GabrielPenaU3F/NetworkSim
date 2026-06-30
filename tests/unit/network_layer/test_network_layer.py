import numpy as np
import pytest

from src.network_layer.packets import IPPacket
from src.utils import serialize_ip_address, int_to_bits
from tests.utilities.dummies import DummyInterface
from unittest.mock import Mock


@pytest.fixture
def dummy_interface_with_peer():
    interface = DummyInterface()
    interface.mac_address = '02:00:00:00:00:01'

    peer_interface = DummyInterface()
    peer_interface.mac_address = '02:00:00:00:00:02'

    mock_link = Mock()
    mock_link.get_other_interface.return_value = peer_interface
    interface.link = mock_link

    return interface

@pytest.fixture
def last_packet_for_me(tile_bits):
    return IPPacket('127.0.0.1', '192.168.0.1', 1, 0, 8, tile_bits(4))

@pytest.fixture
def nonlast_packet_for_me(tile_bits):
    return IPPacket('127.0.0.1', '192.168.0.1', 0, 0, 8, tile_bits(4))

@pytest.fixture
def nonfull_last_packet_for_me(tile_bits):
    return IPPacket('127.0.0.1', '192.168.0.1', 1, 0, 4, np.concatenate((tile_bits(2), np.zeros(4))))


class TestMessageComplete:

    def test_empty_buffer_is_not_complete(self, example_network_layer):
        assert example_network_layer._message_complete() == False

    def test_single_packet_starting_at_zero_is_complete(self, example_network_layer):
        example_network_layer._rx_buffer = {0: np.zeros(8)}
        example_network_layer._last_received = True
        assert example_network_layer._message_complete() == True

    def test_single_packet_not_starting_at_zero_is_not_complete(self, example_network_layer):
        example_network_layer._rx_buffer = {8: np.zeros(8)}
        example_network_layer._last_received = True
        assert example_network_layer._message_complete() == False

    def test_two_contiguous_packets_are_complete(self, example_network_layer):
        example_network_layer._rx_buffer = {0: np.zeros(8), 8: np.zeros(8)}
        example_network_layer._last_received = True
        assert example_network_layer._message_complete() == True

    def test_two_packets_with_hole_are_not_complete(self, example_network_layer):
        example_network_layer._rx_buffer = {0: np.zeros(8), 16: np.zeros(8)}
        example_network_layer._last_received = True
        assert example_network_layer._message_complete() == False

    def test_three_contiguous_packets_are_complete(self, example_network_layer):
        example_network_layer._rx_buffer = {0: np.zeros(8), 8: np.zeros(8), 16: np.zeros(8)}
        example_network_layer._last_received = True
        assert example_network_layer._message_complete() == True

    def test_three_packets_with_missing_middle_are_not_complete(self, example_network_layer):
        example_network_layer._rx_buffer = {0: np.zeros(8), 16: np.zeros(8)}
        example_network_layer._last_received = True
        assert example_network_layer._message_complete() == False


class TestRebuildMessage:

    def test_single_fragment_is_rebuilt_correctly(self, example_network_layer):
        payload = np.tile([0, 1], 4)
        example_network_layer._rx_buffer = {0: (payload, 8)}
        result = example_network_layer._rebuild_message()
        assert np.all(result == payload)

    def test_two_fragments_are_rebuilt_in_correct_order(self, example_network_layer):
        payload_1 = np.tile([0, 1], 4)
        payload_2 = np.tile([1, 0], 4)
        example_network_layer._rx_buffer = {0: (payload_1, 8), 8: (payload_2, 8)}
        result = example_network_layer._rebuild_message()
        expected = np.concatenate([payload_1, payload_2])
        assert np.all(result == expected)

    def test_fragments_arriving_out_of_order_are_rebuilt_correctly(self, example_network_layer):
        payload_1 = np.tile([0, 1], 4)
        payload_2 = np.tile([1, 0], 4)
        # buffer desordenado
        example_network_layer._rx_buffer = {8: (payload_2, 8), 0: (payload_1, 8)}
        result = example_network_layer._rebuild_message()
        expected = np.concatenate([payload_1, payload_2])
        assert np.all(result == expected)

    def test_buffer_is_cleared_after_rebuild(self, example_network_layer):
        example_network_layer._rx_buffer = {0: (np.zeros(8), 0)}
        example_network_layer._rebuild_message()
        assert example_network_layer._rx_buffer == {}

    def test_last_received_flag_is_reset_after_rebuild(self, example_network_layer):
        example_network_layer._rx_buffer = {0: (np.zeros(8), 0)}
        example_network_layer._last_received = True
        example_network_layer._rebuild_message()
        assert example_network_layer._last_received == False

    def test_payload_is_trimmed_to_real_length(self, example_network_layer):
        expected_payload = np.tile([1, 0], 2).astype(np.uint8)
        payload_last = np.array([1, 0, 1, 0, 0, 0, 0, 0], dtype=np.uint8)
        example_network_layer._rx_buffer = {0: (payload_last, 4)}
        assert np.all(example_network_layer._trim_payload(0) == expected_payload)

    def test_complete_payload_is_not_trimmed(self, example_network_layer):
        expected_payload = np.tile([1, 0], 4).astype(np.uint8)
        example_network_layer._rx_buffer = {0: (expected_payload, 8)}
        assert np.all(example_network_layer._trim_payload(0) == expected_payload)

    def test_last_fragment_is_trimmed_to_real_length(self, example_network_layer):
        payload_1 = np.tile([0, 1], 4)  # 8 bits reales
        payload_last = np.array([1, 0, 1, 0, 0, 0, 0, 0], dtype=np.uint8)
        example_network_layer._rx_buffer = {0: (payload_1, 8), 8: (payload_last, 4)}
        result = example_network_layer._rebuild_message()
        expected = np.concatenate([payload_1, payload_last[:4]])
        assert np.all(result == expected)


class TestNetworkLayerTX:

    def test_transmit_sends_bits_downward(self, network_layer_with_dummy_lower, tile_bits, dummy_interface_with_peer):
        layer, dummy = network_layer_with_dummy_lower
        bits = tile_bits(4)  # 1 packet
        layer.transmit(bits, interface=dummy_interface_with_peer, dst_mac='02:00:00:00:00:02')
        assert dummy.calls == 1

    def test_transmit_sends_one_call_per_packet(self, network_layer_with_dummy_lower, tile_bits, dummy_interface_with_peer):
        layer, dummy = network_layer_with_dummy_lower
        bits = tile_bits(8)  # 2 packets
        layer.transmit(bits, interface=dummy_interface_with_peer, dst_mac='02:00:00:00:00:02')
        assert dummy.calls == 2

    def test_transmit_sends_correct_bit_length(self, network_layer_with_dummy_lower, tile_bits, dummy_interface_with_peer):
        layer, dummy = network_layer_with_dummy_lower
        bits = tile_bits(4)  # 1 packet
        layer.transmit(bits, interface=dummy_interface_with_peer, dst_mac='02:00:00:00:00:02')
        module = layer._ip_module
        expected_size = module.address_size * 2 + 1 + module.offset_size + module.real_length_size + module.packet_payload_size
        assert len(dummy.sent_bits[0]) == expected_size


class TestNetworkLayerRX:

    def test_packet_for_this_node_is_accepted(self, network_layer_with_dummy_lower, last_packet_for_me):
        layer, dummy = network_layer_with_dummy_lower

        bits = layer._ip_module.serialize_packet(last_packet_for_me)
        result = layer.on_receive(bits)
        assert result is not None

    def test_single_packet_message_is_reconstructed(self, network_layer_with_dummy_lower, last_packet_for_me):
        layer, dummy = network_layer_with_dummy_lower
        bits = layer._ip_module.serialize_packet(last_packet_for_me)
        result = layer.on_receive(bits)
        assert np.all(result == last_packet_for_me.payload)

    def test_incomplete_message_returns_none(self, network_layer_with_dummy_lower, nonlast_packet_for_me):
        layer, dummy = network_layer_with_dummy_lower
        bits = layer._ip_module.serialize_packet(nonlast_packet_for_me)
        result = layer.on_receive(bits)
        assert result is None

    def test_incomplete_packet_message_is_correctly_reconstructed(self, network_layer_with_dummy_lower,
                                                                  nonfull_last_packet_for_me, tile_bits):
        layer, dummy = network_layer_with_dummy_lower
        bits = layer._ip_module.serialize_packet(nonfull_last_packet_for_me)
        result = layer.on_receive(bits)
        assert np.all(result == tile_bits(2))

    def test_two_packet_message_is_reconstructed(self, network_layer_with_dummy_lower):
        layer, dummy = network_layer_with_dummy_lower
        payload_1 = np.tile([0, 1], 4)  # 8 bits
        payload_2 = np.tile([1, 0], 4)  # 8 bits
        packet_1 = IPPacket('127.0.0.1', '192.168.0.1', offset=0, is_last=0, real_length=8, payload=payload_1)
        packet_2 = IPPacket('127.0.0.1', '192.168.0.1', offset=8, is_last=1, real_length=8, payload=payload_2)

        bits_1 = layer._ip_module.serialize_packet(packet_1)
        bits_2 = layer._ip_module.serialize_packet(packet_2)
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

        bits_1 = layer._ip_module.serialize_packet(packet_1)
        bits_2 = layer._ip_module.serialize_packet(packet_2)
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
        bits_2 = layer._ip_module.serialize_packet(packet_2)
        bits_1 = layer._ip_module.serialize_packet(packet_1)
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
        bits_3 = layer._ip_module.serialize_packet(packet_3)
        bits_1 = layer._ip_module.serialize_packet(packet_1)
        bits_2 = layer._ip_module.serialize_packet(packet_2)
        layer.on_receive(bits_3)
        layer.on_receive(bits_1)
        result = layer.on_receive(bits_2)
        expected = np.concatenate([payload_1, payload_2, payload_3])
        assert np.all(result == expected)
