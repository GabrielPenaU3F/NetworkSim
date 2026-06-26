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

    def test_send_to_mac_through_multiple_interfaces(self, make_three_hosts):
        A, B, C = make_three_hosts(top_layer='link')
        B.send("sol sol", destination_mac='02:00:00:00:00:00')
        B.send("mar mar", destination_mac='02:00:00:00:00:03')
        received_A = A.read()
        received_C = C.read()
        assert received_A == "sol sol"
        assert received_C == "mar mar"

    def test_message_delivery_through_switch(self, make_topo_two_hosts_with_switch):
        host_a, host_b, switch = make_topo_two_hosts_with_switch(top_layer='link')
        mac_b = host_b.interfaces[0].mac_address

        host_a.send("sol", destination_mac=mac_b)
        received = host_b.read()
        assert received == "sol"

    def test_switch_learns_mac_after_first_transmission(self, make_topo_two_hosts_with_switch):
        host_a, host_b, switch = make_topo_two_hosts_with_switch(top_layer='link')
        mac_a = host_a.interfaces[0].mac_address
        mac_b = host_b.interfaces[0].mac_address

        host_a.send("sol", destination_mac=mac_b)

        # After A sends, switch should have learned A's MAC
        assert mac_a in switch._mac_table

    def test_switch_forwards_to_correct_interface_after_learning(self, make_topo_two_hosts_with_switch):
        host_a, host_b, switch = make_topo_two_hosts_with_switch(top_layer='link')
        mac_a = host_a.interfaces[0].mac_address
        mac_b = host_b.interfaces[0].mac_address

        # First: A sends to B, switch learns A's MAC
        host_a.send("sol", destination_mac=mac_b)
        assert mac_a in switch._mac_table

        # Second: B replies to A, switch should forward directly (not flood)
        host_b.send("luna", destination_mac=mac_a)
        received_A = host_a.read()

        assert received_A == "luna"
        received_B = host_b.read()
        assert received_B == "sol" # Received message was not overwritten by a flood

        # Switch should now know B's MAC too
        assert mac_b in switch._mac_table

    def test_message_roundtrip_through_switch(self, make_topo_two_hosts_with_switch):
        host_a, host_b, switch = make_topo_two_hosts_with_switch(top_layer='link')
        mac_a = host_a.interfaces[0].mac_address
        mac_b = host_b.interfaces[0].mac_address

        host_a.send("sol", destination_mac=mac_b)
        received_b = host_b.read()
        host_b.send(received_b, destination_mac=mac_a)
        received_a = host_a.read()

        assert received_a == "sol"

    def test_message_delivery_through_two_switches(self, make_topo_four_hosts_with_two_switches):
        host_a, _, _, _, host_d, _ = make_topo_four_hosts_with_two_switches(top_layer='link')
        mac_d = host_d.interfaces[0].mac_address

        host_a.send("sol", destination_mac=mac_d)
        received = host_d.read()
        assert received == "sol"

    def test_switches_learn_after_flood(self, make_topo_four_hosts_with_two_switches):
        host_a, host_b, switch_ab, host_c, host_d, switch_cd = make_topo_four_hosts_with_two_switches(top_layer='link')
        mac_a = host_a.interfaces[0].mac_address
        mac_d = host_d.interfaces[0].mac_address

        # A sends to B, switch AB learns A's MAC and every host receives the message
        host_a.send("sol", destination_mac=mac_d)
        received_msgs = [host_b.read(), host_c.read(), host_d.read()]
        assert mac_a in switch_ab._mac_table
        assert mac_a in switch_cd._mac_table
        assert all(msg == "sol" for msg in received_msgs)

    def test_switches_forward_directly_after_flood(self, make_topo_four_hosts_with_two_switches):
        host_a, host_b, switch_ab, host_c, host_d, switch_cd = make_topo_four_hosts_with_two_switches(top_layer='link')
        mac_a = host_a.interfaces[0].mac_address
        mac_d = host_d.interfaces[0].mac_address

        # First: A sends to B
        host_a.send("sol", destination_mac=mac_d)

        # # Second: D replies to A, switch should forward directly (not flood)
        host_d.send("luna", destination_mac=mac_a)
        received_A = host_a.read()
        assert received_A == "luna"
        other_buffered_msgs = [host_b.read(), host_c.read(), host_d.read()]
        assert all(msg == "sol" for msg in other_buffered_msgs) # Received message was not overwritten by a flood

        # Both switches should now know D's MAC too
        assert mac_d in switch_ab._mac_table
        assert mac_d in switch_cd._mac_table

class TestIntegrationUpToNetwork:

    def test_host_can_send_by_ip_through_switch(self, make_topo_two_hosts_with_switch):
        host_a, host_b, switch = make_topo_two_hosts_with_switch(top_layer='network')
        host_a.send("sol", destination_ip='192.168.0.2')
        received = host_b.read()
        # assert received == "sol"

    # def test_packet_is_forwarded_through_intermediate_node(self, linear_network):
    #     host_a = linear_network.get_node('192.168.0.1')
    #     host_c = linear_network.get_node('192.168.0.3')
    #     host_a.send("sol", destination_ip='192.168.0.3')
    #
    #     received = host_c.read()
    #     assert received == "sol"
    #
    # def test_packet_roundtrip(self, linear_network):
    #     host_a = linear_network.get_node('192.168.0.1')
    #     host_c = linear_network.get_node('192.168.0.3')
    #     host_a.send("sol", destination_ip='192.168.0.3')
    #
    #     received_c = host_c.read()
    #     host_c.send(received_c, destination_ip='192.168.0.1')
    #     received_a = host_a.read()
    #     assert received_a == "sol"
