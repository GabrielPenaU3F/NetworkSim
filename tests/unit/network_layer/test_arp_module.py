import numpy as np
import pytest

from network_layer.network_modules.arp_module import ARPModule, ARP_ACTION_SEND_REPLY, ARP_ACTION_REPLY_RECEIVED
from network_layer.packets import ARPPacket
from protocol_constants import ethernet, ip, arp
from utils import deserialize_mac_address, deserialize_ip_address


@pytest.fixture
def arp_module():
    return ARPModule(mac_address_size=ethernet.MAC_SIZE, ip_address_size=ip.IP_SIZE)

@pytest.fixture
def example_request():
    return ARPPacket(
        operation=arp.ARP_REQUEST,
        sender_mac='02:00:00:00:00:01',
        sender_ip='192.168.0.1',
        target_mac='00:00:00:00:00:00',
        target_ip='192.168.0.2'
    )

@pytest.fixture
def example_reply():
    return ARPPacket(
        operation=arp.ARP_REPLY,
        sender_mac='02:00:00:00:00:02',
        sender_ip='192.168.0.2',
        target_mac='02:00:00:00:00:01',
        target_ip='192.168.0.1'
    )


class TestARPSerialization:

    def test_serialized_size_is_correct(self, arp_module, example_request):
        bits = arp_module.serialize_packet(example_request)
        expected_size = 1 + ethernet.MAC_SIZE + 32 + ethernet.MAC_SIZE + ip.IP_SIZE
        assert len(bits) == expected_size

    def test_serialize_operation_request(self, arp_module, example_request):
        bits = arp_module.serialize_packet(example_request)
        assert bits[0] == arp.ARP_REQUEST

    def test_serialize_operation_reply(self, arp_module, example_reply):
        bits = arp_module.serialize_packet(example_reply)
        assert bits[0] == arp.ARP_REPLY

    def test_serialize_sender_mac(self, arp_module, example_request):
        bits = arp_module.serialize_packet(example_request)
        sender_mac = deserialize_mac_address(bits[1:1 + ethernet.MAC_SIZE])
        assert sender_mac == '02:00:00:00:00:01'

    def test_serialize_sender_ip(self, arp_module, example_request):
        bits = arp_module.serialize_packet(example_request)
        sender_ip_start = 1 + ethernet.MAC_SIZE
        sender_ip = deserialize_ip_address(bits[sender_ip_start:sender_ip_start + ip.IP_SIZE], num_parts=4)
        assert sender_ip == '192.168.0.1'

    def test_serialize_target_mac(self, arp_module, example_request):
        bits = arp_module.serialize_packet(example_request)
        target_mac_start = 1 + ethernet.MAC_SIZE + ip.IP_SIZE
        target_mac = deserialize_mac_address(bits[target_mac_start:target_mac_start + ethernet.MAC_SIZE])
        assert target_mac == '00:00:00:00:00:00'

    def test_serialize_target_ip(self, arp_module, example_request):
        bits = arp_module.serialize_packet(example_request)
        target_ip_start = 1 + ethernet.MAC_SIZE + ip.IP_SIZE + ethernet.MAC_SIZE
        target_ip = deserialize_ip_address(bits[target_ip_start:target_ip_start + ip.IP_SIZE], num_parts=4)
        assert target_ip == '192.168.0.2'


class TestARPDeserialization:

    def test_deserialize_operation_request(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(0),
            make_ip_for(2)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.operation == arp.ARP_REQUEST

    def test_deserialize_operation_reply(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REPLY], dtype=np.uint8),
            make_mac_for(2),
            make_ip_for(2),
            make_mac_for(1),
            make_ip_for(1)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.operation == arp.ARP_REPLY

    def test_deserialize_sender_mac(self, arp_module, example_request, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(0),
            make_ip_for(2)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.sender_mac == '02:00:00:00:00:01'

    def test_deserialize_sender_ip(self, arp_module, example_request, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(0),
            make_ip_for(2)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.sender_ip == '192.168.0.1'

    def test_deserialize_target_mac(self, arp_module, example_request, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(None),
            make_ip_for(2)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.target_mac == '00:00:00:00:00:00'

    def test_deserialize_target_ip(self, arp_module, example_request, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(0),
            make_ip_for(2)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.target_ip == '192.168.0.2'


class TestARPRoundtrip:

    def test_request_roundtrip(self, arp_module, example_request):
        bits = arp_module.serialize_packet(example_request)
        packet = arp_module.deserialize_packet(bits)
        assert packet.operation == example_request.operation
        assert packet.sender_mac == example_request.sender_mac
        assert packet.sender_ip == example_request.sender_ip
        assert packet.target_mac == example_request.target_mac
        assert packet.target_ip == example_request.target_ip

    def test_reply_roundtrip(self, arp_module, example_reply):
        bits = arp_module.serialize_packet(example_reply)
        packet = arp_module.deserialize_packet(bits)
        assert packet.operation == example_reply.operation
        assert packet.sender_mac == example_reply.sender_mac
        assert packet.sender_ip == example_reply.sender_ip
        assert packet.target_mac == example_reply.target_mac
        assert packet.target_ip == example_reply.target_ip


class TestARPHandleIncomingPacket:

    def test_request_not_for_this_node_is_discarded(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(None),
            make_ip_for(3)  # target is .3
        ])
        result = arp_module.handle_incoming_packet(bits, my_ip='192.168.0.2', my_mac='02:00:00:00:00:02') # node is .2
        assert result is None

    def test_request_is_stored_in_arp_cache(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(2),
            make_ip_for(2),
            make_mac_for(None),
            make_ip_for(1)  # target is us
        ])
        arp_module.handle_incoming_packet(bits, my_ip='192.168.0.1', my_mac='02:00:00:00:00:01')
        assert arp_module._arp_cache['192.168.0.2'] == '02:00:00:00:00:02'

    def test_arp_cache_is_updated_on_reception(self, arp_module, make_mac_for, make_ip_for):
        arp_module._arp_cache['192.168.0.2'] = '02:00:00:00:00:10'
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(2),
            make_ip_for(2),
            make_mac_for(None),
            make_ip_for(1)  # target is us
        ])
        arp_module.handle_incoming_packet(bits, my_ip='192.168.0.1', my_mac='02:00:00:00:00:01')
        assert arp_module._arp_cache['192.168.0.2'] == '02:00:00:00:00:02'

    def test_request_for_this_node_returns_reply(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(None),
            make_ip_for(2)
        ])
        action, reply = arp_module.handle_incoming_packet(bits, my_ip='192.168.0.2', my_mac='02:00:00:00:00:02')
        assert action == ARP_ACTION_SEND_REPLY
        assert type(reply) == ARPPacket
        assert reply.operation == arp.ARP_REPLY

    def test_reply_fills_sender_mac_correctly(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(None),
            make_ip_for(2)
        ])
        action, reply = arp_module.handle_incoming_packet(bits, my_ip='192.168.0.2', my_mac='02:00:00:00:00:02')
        assert reply.sender_mac == '02:00:00:00:00:02'

    def test_reply_fills_sender_ip_correctly(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(None),
            make_ip_for(2)
        ])
        action, reply = arp_module.handle_incoming_packet(bits, my_ip='192.168.0.2', my_mac='02:00:00:00:00:02')
        assert reply.sender_ip == '192.168.0.2'

    def test_reply_targets_original_sender(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            make_mac_for(1),
            make_ip_for(1),
            make_mac_for(None),
            make_ip_for(2)
        ])
        action, reply = arp_module.handle_incoming_packet(bits, my_ip='192.168.0.2', my_mac='02:00:00:00:00:02')
        assert reply.target_mac == '02:00:00:00:00:01'
        assert reply.target_ip == '192.168.0.1'

    def test_reply_is_stored_in_arp_cache(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REPLY], dtype=np.uint8),
            make_mac_for(2),
            make_ip_for(2),
            make_mac_for(1),
            make_ip_for(1)
        ])
        arp_module.handle_incoming_packet(bits, my_ip='192.168.0.1', my_mac='02:00:00:00:00:01')
        assert arp_module._arp_cache['192.168.0.2'] == '02:00:00:00:00:02'

    def test_reply_not_for_this_node_is_discarded(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REPLY], dtype=np.uint8),
            make_mac_for(2),
            make_ip_for(2),
            make_mac_for(3),
            make_ip_for(3)  # target is .3
        ])
        arp_module.handle_incoming_packet(bits, my_ip='192.168.0.1', my_mac='02:00:00:00:00:01') # node is .1
        assert '192.168.0.2' not in arp_module._arp_cache

    def test_reply_for_this_node_returns_action_and_packet(self, arp_module, make_mac_for, make_ip_for):
        bits = np.concatenate([
            np.array([arp.ARP_REPLY], dtype=np.uint8),
            make_mac_for(2),
            make_ip_for(2),
            make_mac_for(1),
            make_ip_for(1)  # target is us
        ])
        result = arp_module.handle_incoming_packet(bits, my_ip='192.168.0.1', my_mac='02:00:00:00:00:01')
        assert result is not None
        action, packet = result
        assert action == ARP_ACTION_REPLY_RECEIVED
        assert packet.operation == arp.ARP_REPLY
        assert packet.sender_ip == '192.168.0.2'
        assert packet.sender_mac == '02:00:00:00:00:02'