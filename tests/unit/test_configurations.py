import numpy as np
import pytest

from src.network_layer.routing import ShortestPathRouting
from src.physical_layer.channel_codes.channel_codes import NoChannelCode
from src.system_configurations.config import ChecksumConfig, EthernetLinkConfig, CRCConfig, NetworkConfig, \
    PacketConfig
from src.system_configurations.config_manager import ConfigManager
from infrastructure.checksum import CRCChecksum, ParityChecksum


@pytest.fixture
def cfg_manager():
    return ConfigManager()


def test_default_top_layer_is_network(cfg_manager):
    assert cfg_manager.top_layer == 'network'

def test_top_layer_can_be_changed():
    cfg_manager = ConfigManager(top_layer='link')
    assert cfg_manager.top_layer == 'link'


class TestInfrastructureConfig:

    def test_default_alphabet_is_the_test_alphpabet(self, cfg_manager):
        infra_cfg = cfg_manager.infrastructure_cfg
        assert infra_cfg.alphabet == 'test_16bits_alph'


class TestPhysicalLayerConfig:

    def test_physical_config_defaults(self, cfg_manager):
        phys = cfg_manager.physical_layer_cfg
        assert phys.channel_code is NoChannelCode

    def test_physical_config_override_does_not_affect_other_parameters(self):
        manager = ConfigManager()
        phys = manager.physical_layer_cfg
        assert phys.channel_code is NoChannelCode


class TestEthernetLinkLayerConfig:

    def test_ethernet_config_defaults(self, cfg_manager):
        eth = cfg_manager.link_layer_cfg
        assert eth.min_payload_bits == 368
        assert eth.max_payload_bits == 12000
        assert eth.mac_size == 48
        assert eth.ether_type_size == 16
        assert eth.real_length_size == 16
        assert eth.checksum_size == 32

    def test_ethernet_config_header_size_is_derived(self, cfg_manager):
        eth = cfg_manager.link_layer_cfg
        assert eth.header_size == 48 * 2 + 16 + 16

    def test_ethernet_config_checksum_defaults(self, cfg_manager):
        eth = cfg_manager.link_layer_cfg
        assert eth.checksum_cfg.cls is ParityChecksum
        assert eth.checksum_cfg.params == {}

    def test_ethernet_config_override(self):
        cfg_manager = ConfigManager(link=EthernetLinkConfig(
            min_payload_bits=8,
            max_payload_bits=16,
        ))
        eth = cfg_manager.link_layer_cfg

        assert eth.min_payload_bits == 8
        assert eth.max_payload_bits == 16

    def test_ethernet_config_override_does_not_affect_other_parameters(self):
        cfg_manager = ConfigManager(link=EthernetLinkConfig(
            min_payload_bits=8,
            max_payload_bits=16,
        ))
        eth = cfg_manager.link_layer_cfg
        assert eth.mac_size == 48
        assert eth.checksum_size == 32

    def test_ethernet_config_with_custom_checksum(self):
        cfg_manager = ConfigManager(link=EthernetLinkConfig(
            checksum_cfg=ChecksumConfig.from_crc(CRCConfig(generator=[1, 0, 0, 1]))
        ))
        eth = cfg_manager.link_layer_cfg
        assert eth.checksum_cfg.cls is CRCChecksum

    def test_ethernet_config_rejects_min_greater_than_max(self):
        with pytest.raises(ValueError, match='min_payload_bits cannot exceed max_payload_bits'):
            EthernetLinkConfig(min_payload_bits=20, max_payload_bits=10)

    def test_ethernet_config_rejects_max_payload_too_large_for_real_length_field(self):
        with pytest.raises(ValueError, match='A real length size of 4 bits cannot represent a payload size of 20 bits'):
            EthernetLinkConfig(min_payload_bits=10, max_payload_bits=20, real_length_size=4)  # max real_length representable is 15

# # Old Link Layer configuration tests
# class TestLinkLayerConfig:
#
#     def test_link_config_defaults(self, cfg_manager):
#         link = cfg_manager.link_layer_cfg
#         assert link.max_retries == 5
#
#     def test_frame_config_defaults(self, cfg_manager):
#         frame_cfg = cfg_manager.link_layer_cfg.frame_cfg
#         assert frame_cfg.payload_size == 8
#         assert frame_cfg.seq_size == 8
#         assert frame_cfg.checksum_size == 4
#
#     def test_link_config_checksum_defaults(self, cfg_manager):
#         cs_cfg = cfg_manager.link_layer_cfg.checksum_cfg
#         assert cs_cfg.cls is ParityChecksum
#         assert cs_cfg.params == {}
#
#     def test_link_config_override(self):
#         manager = ConfigManager(link=LinkConfig(
#                 max_retries=10,
#                 checksum_cfg=ChecksumConfig.from_crc(CRCConfig(generator=[1, 0, 0, 1])),
#             )
#         )
#         link_cfg = manager.link_layer_cfg
#         assert link_cfg.max_retries == 10
#         assert link_cfg.checksum_cfg.cls is CRCChecksum
#         assert np.all(link_cfg.checksum_cfg.params.get('generator') == [1, 0, 0, 1])
#
#     def test_physical_config_override_does_not_affect_other_parameters(self):
#         manager = ConfigManager(link=LinkConfig(
#                 frame_cfg=FrameConfig(
#                     payload_size=16,
#                     seq_size=16,
#                     checksum_size=8,
#                 )
#             )
#         )
#         link_cfg = manager.link_layer_cfg
#         frame_cfg = link_cfg.frame_cfg
#         assert link_cfg.checksum_cfg.cls is ParityChecksum
#         assert frame_cfg.payload_size == 16
#         assert frame_cfg.seq_size == 16
#         assert frame_cfg.checksum_size == 8
#
#     def test_link_config_rejects_invalid_crc_generator(self):
#         manager = ConfigManager(link=LinkConfig(
#                 checksum_cfg=ChecksumConfig.from_crc(CRCConfig(generator=[1, 1, 0]))
#             )
#         )
#         with pytest.raises(ValueError, match='Generator must end with 1'):
#             manager.link_layer_cfg.build_checksum()


class TestNetworkLayerConfig:

    def test_network_config_defaults(self, cfg_manager):
        network = cfg_manager.network_layer_cfg
        assert network.routing is ShortestPathRouting
        assert network.address_size == 32

    def test_packet_config_defaults(self, cfg_manager):
        packet_cfg = cfg_manager.network_layer_cfg.packet_cfg
        assert packet_cfg.payload_size == 64
        assert packet_cfg.offset_size == 16

    def test_link_config_override(self):
        manager = ConfigManager(network=NetworkConfig(
                packet_cfg=PacketConfig(real_length_size=8),
            )
        )
        network_cfg = manager.network_layer_cfg
        assert network_cfg.packet_cfg.real_length_size == 8

    def test_network_config_override_does_not_affect_other_parameters(self):
        manager = ConfigManager(network=NetworkConfig(
                packet_cfg=PacketConfig(real_length_size=16),
            )
        )
        network_cfg = manager.network_layer_cfg
        assert network_cfg.routing is ShortestPathRouting
        assert network_cfg.address_size == 32
        assert network_cfg.packet_cfg.offset_size == 16
        assert network_cfg.packet_cfg.payload_size == 64

    def test_network_config_rejects_invalid_address_size(self):
        with pytest.raises(ValueError, match='Address size must be divisible by 8'):
            manager = ConfigManager(network=NetworkConfig(address_size=12))

    def test_network_config_rejects_invalid_offset_size(self):
        with pytest.raises(ValueError, match=f'An offset size of 4 bits cannot represent '
            f'offsets up to a payload size of 64 bits'):
            manager = ConfigManager(network=NetworkConfig(packet_cfg=PacketConfig(offset_size=4)))

    def test_network_config_rejects_invalid_real_length_size(self):
        with pytest.raises(ValueError, match=f'Real length size should be at least 7 '
                             f'bits to represent 64 payload bits'):
            manager = ConfigManager(network=NetworkConfig(packet_cfg=PacketConfig(real_length_size=2)))