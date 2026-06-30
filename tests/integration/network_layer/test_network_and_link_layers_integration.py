from protocol_constants import ethernet
from tests.utilities.dummies import DummyInterface


class TestEtherTypePropagation:

    def test_ip_packet_is_sent_with_ipv4_ether_type(self, network_layer_with_dummy_lower, tile_bits):
        layer, dummy = network_layer_with_dummy_lower
        bits = tile_bits(4)  # 1 packet
        layer.transmit(bits, interface=DummyInterface(), dst_ip='192.168.0.2', dst_mac='02:00:00:00:00:02')

        assert dummy.calls == 1
        assert dummy.sent_kwargs[0]['ether_type'] == ethernet.IPV4

    def test_arp_packet_is_sent_with_arp_ether_type(self, network_layer_with_dummy_lower):
        layer, dummy = network_layer_with_dummy_lower
        layer.send_arp_request('192.168.0.2', interface=DummyInterface())
        assert dummy.calls == 1
        assert dummy.sent_kwargs[0]['ether_type'] == ethernet.ARP