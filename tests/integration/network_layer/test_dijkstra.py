from src.infrastructure.channels import BinarySymmetricChannel
from src.infrastructure.network import Network
from src.system_configurations.config_manager import ConfigManager


# def test_packet_is_forwarded_through_intermediate_node():
#     network = Network(ConfigManager(top_layer='network'))
#
#     host_a = network.create_host(address='192.168.0.1')
#     host_b = network.create_host(address='192.168.0.2')
#     host_c = network.create_host(address='192.168.0.3')
#
#     channel = BinarySymmetricChannel(error_prob=0)
#
#     network.connect(host_a, host_b, channel)
#     network.connect(host_b, host_c, channel)
#
#     network.build_routing_tables()
#
#     host_a.send("sol", destination='192.168.0.3')
#     received = host_c.read()
#
#     assert received == "sol"