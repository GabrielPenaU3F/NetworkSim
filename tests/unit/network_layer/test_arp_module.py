import numpy as np
import pytest

from network_layer.network_modules.arp_module import ARPModule
from network_layer.packets import ARPPacket
from protocol_constants import ethernet, ip, arp
from utils import deserialize_mac_address, deserialize_ip_address, serialize_mac_address, serialize_ip_address


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

    def test_deserialize_operation_request(self, arp_module):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            serialize_mac_address('02:00:00:00:00:01', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.1', ip.IP_SIZE),
            serialize_mac_address('00:00:00:00:00:00', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.2', ip.IP_SIZE)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.operation == arp.ARP_REQUEST

    def test_deserialize_operation_reply(self, arp_module):
        bits = np.concatenate([
            np.array([arp.ARP_REPLY], dtype=np.uint8),
            serialize_mac_address('02:00:00:00:00:02', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.2', ip.IP_SIZE),
            serialize_mac_address('02:00:00:00:00:01', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.1', ip.IP_SIZE)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.operation == arp.ARP_REPLY

    def test_deserialize_sender_mac(self, arp_module, example_request):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            serialize_mac_address('02:00:00:00:00:01', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.1', ip.IP_SIZE),
            serialize_mac_address('00:00:00:00:00:00', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.2', ip.IP_SIZE)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.sender_mac == '02:00:00:00:00:01'

    def test_deserialize_sender_ip(self, arp_module, example_request):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            serialize_mac_address('02:00:00:00:00:01', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.1', ip.IP_SIZE),
            serialize_mac_address('00:00:00:00:00:00', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.2', ip.IP_SIZE)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.sender_ip == '192.168.0.1'

    def test_deserialize_target_mac(self, arp_module, example_request):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            serialize_mac_address('02:00:00:00:00:01', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.1', ip.IP_SIZE),
            serialize_mac_address('00:00:00:00:00:00', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.2', ip.IP_SIZE)
        ])
        packet = arp_module.deserialize_packet(bits)
        assert packet.target_mac == '00:00:00:00:00:00'

    def test_deserialize_target_ip(self, arp_module, example_request):
        bits = np.concatenate([
            np.array([arp.ARP_REQUEST], dtype=np.uint8),
            serialize_mac_address('02:00:00:00:00:01', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.1', ip.IP_SIZE),
            serialize_mac_address('00:00:00:00:00:00', ethernet.MAC_SIZE),
            serialize_ip_address('192.168.0.2', ip.IP_SIZE)
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
