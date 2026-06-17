import pytest

from infrastructure.network import Network
from system_configurations.config_manager import ConfigManager


@pytest.fixture
def make_two_hosts(clean_channel):
    def _make(top_layer):
        cfg_manager = ConfigManager(top_layer=top_layer)
        network = Network(cfg_manager)
        A = network.create_host()
        B = network.create_host()
        network.connect(A, B, clean_channel)
        return A, B
    return _make

@pytest.fixture
def make_triangle_hosts(clean_channel):
    def _make(top_layer):
        cfg_manager = ConfigManager(top_layer=top_layer)
        network = Network(cfg_manager)
        A = network.create_host()
        B = network.create_host()
        C = network.create_host()
        network.connect(A, B, clean_channel)
        network.connect(B, C, clean_channel)
        network.connect(C, A, clean_channel)
        return A, B, C
    return _make

# class TestIntegrationPhysicalOnly:
#
#     def test_message_delivery(self, make_two_hosts):
#         A, B = make_two_hosts(top_layer='physical')
#         A.send("sol")
#         received = B.read()
#         assert received == "sol"
#
#     def test_large_message_delivery(self, make_two_hosts):
#         A, B = make_two_hosts(top_layer='physical')
#         A.send("sol sol mar viento")
#         received = B.read()
#         assert received == "sol sol mar viento"
#

# class TestIntegrationUpToLink:
#
#     def test_message_delivery(self, make_two_hosts):
#         A, B = make_two_hosts(top_layer='link')
#         A.send("sol")
#         received = B.read()
#         assert received == "sol"
#
#     def test_medium_message_delivery(self, make_two_hosts):
#         A, B = make_two_hosts(top_layer='link')
#         A.send("sol luna")
#         received = B.read()
#         assert received == "sol luna"
#
#     def test_large_message_delivery(self, make_two_hosts):
#         A, B = make_two_hosts(top_layer='link')
#         A.send("sol sol mar viento")
#         received = B.read()
#         assert received == "sol sol mar viento"
#
#     def test_large_message_triangle_delivery(self, make_triangle_hosts):
#         A, B, C = make_triangle_hosts(top_layer='link')
#         A.send("sol sol mar viento", 0)
#         received_B = B.read()
#         B.send(received_B, 1)
#         received_C = C.read()
#         C.send(received_C, 1)
#         received = A.read()
#         assert received == "sol sol mar viento"
#
#     def test_large_message_roundtrip(self, make_two_hosts):
#         A, B = make_two_hosts(top_layer='link')
#         A.send("sol sol mar viento")
#         received_B = B.read()
#         B.send(received_B)
#         received_A = A.read()
#         assert received_A == "sol sol mar viento"
#
#     def test_large_message_roundtrip_and_send_again(self, make_two_hosts):
#         A, B = make_two_hosts(top_layer='link')
#         A.send("sol sol mar viento")
#         received_B_1 = B.read()
#         B.send(received_B_1)
#         received_A = A.read()
#         A.send(received_A)
#         received_B_2 = B.read()
#         assert received_B_2 == "sol sol mar viento"
#
#
class TestIntegrationUpToNetwork:

    def test_packet_is_forwarded_through_intermediate_node(self, linear_network):
        host_a = linear_network.get_node('192.168.0.1')
        host_c = linear_network.get_node('192.168.0.3')
        host_a.send("sol", destination_address='192.168.0.3')

        received = host_c.read()
        assert received == "sol"

    def test_packet_roundtrip(self, linear_network):
        host_a = linear_network.get_node('192.168.0.1')
        host_c = linear_network.get_node('192.168.0.3')
        host_a.send("sol", destination_address='192.168.0.3')

        received_c = host_c.read()
        host_c.send(received_c, destination_address='192.168.0.1')
        received_a = host_a.read()
        assert received_a == "sol"
