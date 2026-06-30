import numpy as np
import pytest

from protocol_constants import ethernet
from protocol_constants.arp import ARP_REQUEST, ARP_REPLY
from src.errors import NetworkError
from src.network_layer.packets import IPPacket, ARPPacket


@pytest.fixture
def example_ip_packet():
    origin = '192.168.0.1'
    destiny = '192.168.0.2'
    payload = np.array([1, 0, 1, 0], dtype=np.uint8)
    return IPPacket(origin, destiny, is_last=0, offset=0, real_length=4, payload=payload)

@pytest.fixture
def make_example_arp_packet():
    def _make(operation):
        sender_ip = '192.168.0.1'
        target_ip = '192.168.0.2'
        sender_mac = '02:00:00:00:00:01'
        target_mac = '02:00:00:00:00:02'
        return ARPPacket(operation, sender_mac, sender_ip, target_mac, target_ip)
    return _make


class TestIPPacket:

    def test_ip_packet_has_correct_ethernet_type(self, example_ip_packet):
        assert example_ip_packet.ether_type == ethernet.IPV4

    def test_ip_packet_knows_origin_address(self, example_ip_packet):
        assert example_ip_packet.origin_address == '192.168.0.1'

    def test_ip_packet_knows_destination_address(self, example_ip_packet):
        assert example_ip_packet.destination_address == '192.168.0.2'

    def test_ip_packet_payload(self, example_ip_packet):
        assert np.all(example_ip_packet.payload == [1, 0, 1, 0])

    def test_cannot_create_ip_packet_without_origin_address(self):
        with pytest.raises(NetworkError, match='Origin and Destination addresses must be specified'):
            IPPacket(None, '192.168.0.1', 0, 0, 1, np.array([1, 0], dtype=np.uint8))

    def test_cannot_create_ip_packet_without_destination_address(self):
        with pytest.raises(NetworkError, match='Origin and Destination addresses must be specified'):
            IPPacket('192.168.0.1', None, 0, 0, 1, np.array([1, 0], dtype=np.uint8))


class TestARPPacket:

    def test_arp_packet_has_correct_ethernet_type(self, make_example_arp_packet):
        packet = make_example_arp_packet(operation=ARP_REQUEST)
        assert packet.ether_type == ethernet.ARP

    def test_arp_packet_knows_sender_addresses(self, make_example_arp_packet):
        packet = make_example_arp_packet(operation=ARP_REQUEST)
        assert packet.sender_ip == '192.168.0.1'
        assert packet.sender_mac == '02:00:00:00:00:01'

    def test_arp_packet_knows_target_addresses(self, make_example_arp_packet):
        packet = make_example_arp_packet(operation=ARP_REQUEST)
        assert packet.target_ip == '192.168.0.2'
        assert packet.target_mac == '02:00:00:00:00:02'

    def test_arp_packet_knows_operation(self, make_example_arp_packet):
        request_packet = make_example_arp_packet(operation=ARP_REQUEST)
        reply_packet = make_example_arp_packet(operation=ARP_REPLY)
        assert request_packet.operation == ARP_REQUEST
        assert reply_packet.operation == ARP_REPLY

    def test_cannot_create_arp_packet_without_operation(self, make_example_arp_packet):
        with pytest.raises(NetworkError, match='All ARP fields must be specified'):
            make_example_arp_packet(operation=None)

    def test_cannot_create_arp_packet_without_sender_addresses(self):
        with pytest.raises(NetworkError, match='All ARP fields must be specified'):
            ARPPacket(sender_ip=None, sender_mac='02:00:00:00:00:01',
                      target_ip='192.168.0.2', target_mac='02:00:00:00:00:02',
                      operation=ARP_REQUEST)

        with pytest.raises(NetworkError, match='All ARP fields must be specified'):
            ARPPacket(sender_ip='192.168.0.1', sender_mac=None,
                      target_ip='192.168.0.2', target_mac='02:00:00:00:00:02',
                      operation=ARP_REQUEST)

    def test_cannot_create_arp_packet_without_target_addresses(self):
        with pytest.raises(NetworkError, match='All ARP fields must be specified'):
            ARPPacket(sender_ip='192.168.0.1', sender_mac='02:00:00:00:00:01',
                      target_ip=None, target_mac='02:00:00:00:00:02',
                      operation=ARP_REQUEST)

        with pytest.raises(NetworkError, match='All ARP fields must be specified'):
            ARPPacket(sender_ip='192.168.0.1', sender_mac='02:00:00:00:00:01',
                      target_ip='192.168.0.2', target_mac=None,
                      operation=ARP_REQUEST)
