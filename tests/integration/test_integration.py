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

    def test_send_to_indexed_interfaces(self, make_three_hosts):
        A, B, C = make_three_hosts(top_layer='physical')
        B.send("sol sol", interface_idx=0)
        B.send("mar mar", interface_idx=1)
        received_A = A.read()
        received_C = C.read()
        assert received_A == "sol sol"
        assert received_C == "mar mar"


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

    def test_cannot_deliver_to_indirectly_connected_host(self, make_triangle_hosts):
        A, B, C = make_triangle_hosts(top_layer='link')
        with pytest.raises(AddressError, match='Destination MAC is not connected to this host'):
            A.send("sol sol mar viento", destination_mac='02:00:00:00:00:03')

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

    def test_send_to_mac_through_multiple_interfaces(self, make_three_hosts):
        A, B, C = make_three_hosts(top_layer='link')
        B.send("sol sol", destination_mac='02:00:00:00:00:00')
        B.send("mar mar", destination_mac='02:00:00:00:00:03')
        received_A = A.read()
        received_C = C.read()
        assert received_A == "sol sol"
        assert received_C == "mar mar"

    # def test_message_delivery_through_switch(self, network_with_switch):
    #     host_a, host_b, switch = network_with_switch
    #     mac_b = host_b.interfaces[0].mac_address
    #
    #     host_a.send("sol", destination_mac=mac_b)
    #     received = host_b.read()
    #     assert received == "sol"
    #
    # def test_switch_learns_mac_after_first_transmission(self, network_with_switch):
    #     network, host_a, host_b, switch = network_with_switch
    #     mac_a = host_a.interfaces[0].mac_address
    #     mac_b = host_b.interfaces[0].mac_address
    #
    #     host_a.send("sol", destination_mac=mac_b)
    #
    #     # After A sends, switch should have learned A's MAC
    #     assert mac_a in switch._mac_table
    #
    # def test_switch_forwards_to_correct_interface_after_learning(self, network_with_switch):
    #     network, host_a, host_b, switch = network_with_switch
    #     mac_a = host_a.interfaces[0].mac_address
    #     mac_b = host_b.interfaces[0].mac_address
    #
    #     # First: A sends to B, switch learns A's MAC
    #     host_a.send("sol", destination_mac=mac_b)
    #     host_b.read()
    #
    #     # Second: B replies to A, switch should forward directly (not flood)
    #     host_b.send("luna", destination_mac=mac_a)
    #     received = host_a.read()
    #
    #     assert received == "luna"
    #     # Switch should now know both MACs
    #     assert mac_a in switch._mac_table
    #     assert mac_b in switch._mac_table
    #
    # def test_message_roundtrip_through_switch(self, network_with_switch):
    #     network, host_a, host_b, switch = network_with_switch
    #     mac_a = host_a.interfaces[0].mac_address
    #     mac_b = host_b.interfaces[0].mac_address
    #
    #     host_a.send("sol", destination_mac=mac_b)
    #     received_b = host_b.read()
    #     host_b.send(received_b, destination_mac=mac_a)
    #     received_a = host_a.read()
    #
    #     assert received_a == "sol"


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
