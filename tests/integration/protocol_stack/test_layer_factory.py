import numpy as np

from infrastructure.checksum import CRCChecksum
from src.link_layer.link_layer import LinkLayer
from src.network_layer.network_layer import NetworkLayer
from src.physical_layer.channel_codes.channel_codes import NoChannelCode, HammingChannelCode
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.layer_factory import LayerFactory
from src.system_configurations.config import PhysicalConfig, EthernetLinkConfig, NetworkConfig, \
    IPPacketConfig, ChecksumConfig
from src.system_configurations.config_manager import ConfigManager

class TestPhysicalLayerBuilder:

    def test_builds_physical_layer_instance(self):
        config = ConfigManager(top_layer='physical')
        layer = LayerFactory.build_physical_layer(config)
        assert type(layer) is PhysicalLayer

    def test_physical_layer_has_correct_channel_code(self):
        config = ConfigManager(top_layer='physical')
        layer = LayerFactory.build_physical_layer(config)
        assert type(layer.channel_code) is NoChannelCode

    def test_physical_layer_channel_code_follows_config(self):
        config = ConfigManager(top_layer='physical',
                                   physical=PhysicalConfig(channel_code=HammingChannelCode)
                               )
        layer = LayerFactory.build_physical_layer(config)
        assert type(layer.channel_code) is HammingChannelCode


# # #This will possibly be used on a future TransportLayer
# class TestLinkLayerBuilder:
#
#     def test_builds_link_layer_instance(self):
#         config = ConfigManager(top_layer='link')
#         layer = LayerFactory.build_link_layer(config)
#         assert type(layer) is LinkLayer
#
#     def test_link_layer_has_correct_checksum(self):
#         config = ConfigManager(top_layer='link',
#                                    link=LinkConfig(checksum_cfg=ChecksumConfig(
#                                            cls=CRCChecksum,
#                                            params={'generator': [1, 0, 0, 1]},
#                                        )
#                                    )
#                                )
#         layer = LayerFactory.build_link_layer(config)
#         assert type(layer.checksum) is CRCChecksum
#         assert np.all(layer.checksum.generator == [1, 0, 0, 1])
#
#     def test_link_layer_has_correct_max_retries(self):
#         config = ConfigManager(top_layer='link',
#                                link=LinkConfig(max_retries=10))
#         layer = LayerFactory.build_link_layer(config)
#         assert layer.max_retries == 10
#
#     def test_link_layer_has_correct_payload_size(self):
#         config = ConfigManager(top_layer='link', link=LinkConfig(
#                                        frame_cfg=FrameConfig(payload_size=16)
#                                    )
#                                )
#         layer = LayerFactory.build_link_layer(config)
#         assert layer.payload_size == 16
#
#     def test_link_layer_has_correct_seq_size(self):
#         config = ConfigManager(top_layer='link', link=LinkConfig(
#                                         frame_cfg=FrameConfig(seq_size=4)
#                                    )
#                                )
#         layer = LayerFactory.build_link_layer(config)
#         assert layer.seq_size == 4


class TestEthernetLinkLayerBuilder:

    def test_builds_link_layer_instance(self):
        config = ConfigManager(top_layer='link')
        layer = LayerFactory.build_link_layer(config)
        assert type(layer) is LinkLayer

    def test_link_layer_has_correct_checksum(self):
        config = ConfigManager(top_layer='link',
                               link=EthernetLinkConfig(checksum_cfg=ChecksumConfig(
                                       cls=CRCChecksum,
                                       params={'generator': [1, 0, 0, 1]},
                                   )
                               )
                           )
        link_module = LayerFactory.build_link_layer(config)._link_module
        assert type(link_module.checksum) is CRCChecksum
        assert np.all(link_module.checksum.generator == [1, 0, 0, 1])

    def test_link_layer_has_correct_min_payload_bits(self):
        config = ConfigManager(top_layer='link',
                               link=EthernetLinkConfig(min_payload_bits=8, max_payload_bits=16))
        link_module = LayerFactory.build_link_layer(config)._link_module
        assert link_module.min_payload_bits == 8

    def test_link_layer_has_correct_max_payload_bits(self):
        config = ConfigManager(top_layer='link',
                               link=EthernetLinkConfig(min_payload_bits=8, max_payload_bits=16))
        link_module = LayerFactory.build_link_layer(config)._link_module
        assert link_module.max_payload_bits == 16

    def test_link_layer_has_correct_mac_size(self):
        config = ConfigManager(top_layer='link',
                               link=EthernetLinkConfig(mac_size=32))
        link_module = LayerFactory.build_link_layer(config)._link_module
        assert link_module.mac_size == 32

    def test_link_layer_has_correct_ether_type_size(self):
        config = ConfigManager(top_layer='link',
                               link=EthernetLinkConfig(ether_type_size=8))
        link_module = LayerFactory.build_link_layer(config)._link_module
        assert link_module.ether_type_size == 8

    def test_link_layer_has_correct_real_length_size(self):
        config = ConfigManager(top_layer='link',
                               link=EthernetLinkConfig(real_length_size=12, max_payload_bits=400))
        link_module = LayerFactory.build_link_layer(config)._link_module
        assert link_module.real_length_size == 12

    def test_link_layer_has_correct_checksum_size(self):
        config = ConfigManager(top_layer='link',
                               link=EthernetLinkConfig(checksum_size=16))
        link_module = LayerFactory.build_link_layer(config)._link_module
        assert link_module.checksum_size == 16

    def test_link_layer_has_physical_layer_below(self):
        config = ConfigManager(top_layer='link')
        layer = LayerFactory.build_link_layer(config)
        assert type(layer.lower_layer) is PhysicalLayer


class TestNetworkLayerBuilder:

    def test_builds_network_layer_instance(self, network_cfg_manager):
        layer = LayerFactory.build_network_layer(network_cfg_manager)
        assert type(layer) is NetworkLayer

    def test_network_layer_has_link_layer_below(self, network_cfg_manager):
        layer = LayerFactory.build_network_layer(network_cfg_manager)
        assert type(layer.lower_layer) is LinkLayer

    def test_network_layer_has_correct_address(self, network_cfg_manager):
        layer = LayerFactory.build_network_layer(network_cfg_manager, address='192.168.0.1')
        assert layer._ip_module.ip == '192.168.0.1'

    def test_network_layer_has_correct_packet_address_size(self):
        config = ConfigManager(top_layer='network',
                               network=NetworkConfig(ip_address_size=64))
        layer = LayerFactory.build_network_layer(config)
        assert layer._ip_module.address_size == 64

    def test_network_layer_has_correct_offset_size(self):
        packet_config = IPPacketConfig(offset_size=8)
        config = ConfigManager(top_layer='network',
                               network=NetworkConfig(packet_cfg=packet_config))
        layer = LayerFactory.build_network_layer(config)
        assert layer._ip_module.offset_size == 8

    def test_network_layer_has_correct_packet_payload_size(self):
        packet_config = IPPacketConfig(payload_size=8)
        config = ConfigManager(top_layer='network',
                               network=NetworkConfig(packet_cfg=packet_config))
        layer = LayerFactory.build_network_layer(config)
        assert layer._ip_module.packet_payload_size == 8
