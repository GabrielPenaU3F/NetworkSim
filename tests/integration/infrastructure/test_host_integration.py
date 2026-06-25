import pytest

from errors import ProtocolError


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