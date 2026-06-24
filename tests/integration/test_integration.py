import pytest

from errors import AddressError


class TestIntegrationPhysicalOnly:

    def test_message_delivery(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='physical')
        A.send("sol")
        received = B.read()
        assert received == "sol"

    def test_large_message_delivery(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='physical')
        A.send("sol sol mar viento")
        received = B.read()
        assert received == "sol sol mar viento"


class TestIntegrationUpToLink:

    def test_message_delivery(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='link')
        A.send("sol", destination_mac='02:00:00:00:00:01')
        received = B.read()
        assert received == "sol"

    def test_medium_message_delivery(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='link')
        A.send("sol luna", destination_mac='02:00:00:00:00:01')
        received = B.read()
        assert received == "sol luna"

    def test_large_message_delivery(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='link')
        A.send("sol sol mar viento", destination_mac='02:00:00:00:00:01')
        received = B.read()
        assert received == "sol sol mar viento"

    def test_cannot_send_to_unknown_mac(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='link')
        with pytest.raises(AddressError, match='Destination MAC is not connected to this host'):
            A.send("sol", destination_mac='02:00:00:00:00:0f')

    def test_large_message_triangle_delivery(self, make_triangle_hosts):
        A, B, C = make_triangle_hosts(top_layer='link')
        A.send("sol sol mar viento", destination_mac='02:00:00:00:00:01')
        received_B = B.read()
        B.send(received_B, destination_mac='02:00:00:00:00:03')
        received_C = C.read()
        C.send(received_C, destination_mac='02:00:00:00:00:05')
        received = A.read()
        assert received == "sol sol mar viento"

    def test_large_message_roundtrip(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='link')
        A.send("sol sol mar viento", destination_mac='02:00:00:00:00:01')
        received_B = B.read()
        B.send(received_B, destination_mac='02:00:00:00:00:00')
        received_A = A.read()
        assert received_A == "sol sol mar viento"

    def test_large_message_roundtrip_and_send_again(self, make_two_hosts):
        A, B = make_two_hosts(top_layer='link')
        A.send("sol sol mar viento", destination_mac='02:00:00:00:00:01')
        received_B_1 = B.read()
        B.send(received_B_1, destination_mac='02:00:00:00:00:00')
        received_A = A.read()
        A.send(received_A, destination_mac='02:00:00:00:00:01')
        received_B_2 = B.read()
        assert received_B_2 == "sol sol mar viento"


class TestIntegrationUpToNetwork:

    def test_packet_is_forwarded_through_intermediate_node(self, linear_network):
        host_a = linear_network.get_node('192.168.0.1')
        host_c = linear_network.get_node('192.168.0.3')
        host_a.send("sol", destination_ip='192.168.0.3')

        received = host_c.read()
        assert received == "sol"

    def test_packet_roundtrip(self, linear_network):
        host_a = linear_network.get_node('192.168.0.1')
        host_c = linear_network.get_node('192.168.0.3')
        host_a.send("sol", destination_ip='192.168.0.3')

        received_c = host_c.read()
        host_c.send(received_c, destination_ip='192.168.0.1')
        received_a = host_a.read()
        assert received_a == "sol"
