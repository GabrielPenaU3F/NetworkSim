import numpy as np
import pytest

from errors import ProtocolError
from network_layer.packets import IPPacket


class TestHostSend:

    def test_physical_send_requires_no_arguments(self, make_two_hosts):
        a, b = make_two_hosts(top_layer='physical')
        a.send('sol')
        # This should not raise any error

    def test_physical_send_with_an_interface_index(self, make_two_hosts):
        a, b = make_two_hosts(top_layer='physical')
        a.send('sol', interface_idx=0)
        # This should not raise any error

    def test_physical_send_to_nonexistent_interface_raises_error(self, make_two_hosts):
        a, b = make_two_hosts(top_layer='physical')
        with pytest.raises(ProtocolError, match='Requested interface does not exist'):
            a.send('sol', interface_idx=1)

    def test_link_send_requires_destination_mac(self, make_two_hosts):
        a, _ = make_two_hosts(top_layer='link')
        with pytest.raises(ProtocolError, match='Destination MAC is required'):
            a.send('sol')

    def test_network_send_requires_destination_ip(self, linear_network):
        a = linear_network.get_node('192.168.0.1')
        with pytest.raises(ProtocolError, match='Destination IP is required'):
            a.send('sol')

    def test_network_host_cannot_forward_packets(self, linear_network):
        a = linear_network.get_node('192.168.0.1')
        c = linear_network.get_node('192.168.0.3')
        a.send('sol', dst_ip='192.168.0.3')
        received = c.read()
        assert received is None

    def test_network_host_discards_packets_for_other_hosts(self, linear_network):
        b = linear_network.get_node('192.168.0.2')
        packet = IPPacket(origin_address='192.168.0.1', destination_address='192.168.0.2',
                          payload=np.zeros(8), is_last=1, real_length=8, offset=0)
        serialized_packet = b._protocol_stack.top_layer._ip_module.serialize_packet(packet)
        b.on_receive(bits=serialized_packet)
        received = b.read()
        assert received is None


class TestHostARPCache:

    def test_host_does_not_know_dst_mac_without_arp(self, linear_network):
        a = linear_network.get_node('192.168.0.1')
        dst_mac = a._get_mac_for_ip('192.168.0.2')
        assert dst_mac is None

    def test_host_knows_cached_dst_mac_after_arp(self, linear_network):
        a = linear_network.get_node('192.168.0.1')
        interface_to_b = a.interfaces[0]
        a._send_arp_request(dst_ip='192.168.0.2', interface=interface_to_b)

        dst_mac = a._get_mac_for_ip('192.168.0.2')
        assert dst_mac == '02:00:00:00:00:01'
