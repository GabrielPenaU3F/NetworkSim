import numpy as np
import pytest

from src.link_layer.checksum import ParityChecksum, CRCChecksum
from src.physical_layer.channel_codes.channel_codes import NoChannelCode
from src.system_configurations.config import ChecksumConfig, LinkConfig, CRCConfig, FrameConfig
from src.system_configurations.config_manager import ConfigManager

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


class TestLinkLayerConfig:

    def test_link_config_defaults(self, cfg_manager):
        link = cfg_manager.link_layer_cfg
        assert link.max_retries == 5

    def test_frame_config_defaults(self, cfg_manager):
        frame_cfg = cfg_manager.link_layer_cfg.frame_cfg
        assert frame_cfg.payload_size == 8
        assert frame_cfg.seq_size == 8
        assert frame_cfg.checksum_size == 4

    def test_link_config_checksum_defaults(self, cfg_manager):
        cs_cfg = cfg_manager.link_layer_cfg.checksum_cfg
        assert cs_cfg.cls is ParityChecksum
        assert cs_cfg.params == {}

    def test_link_config_override(self):
        manager = ConfigManager(link=LinkConfig(
                max_retries=10,
                checksum_cfg=ChecksumConfig.from_crc(CRCConfig(generator=[1, 0, 0, 1])),
            )
        )
        link_cfg = manager.link_layer_cfg
        assert link_cfg.max_retries == 10
        assert link_cfg.checksum_cfg.cls is CRCChecksum
        assert np.all(link_cfg.checksum_cfg.params.get('generator') == [1, 0, 0, 1])

    def test_physical_config_override_does_not_affect_other_parameters(self):
        manager = ConfigManager(link=LinkConfig(
                frame_cfg=FrameConfig(
                    payload_size=16,
                    seq_size=16,
                    checksum_size=8,
                )
            )
        )
        link_cfg = manager.link_layer_cfg
        frame_cfg = link_cfg.frame_cfg
        assert link_cfg.checksum_cfg.cls is ParityChecksum
        assert frame_cfg.payload_size == 16
        assert frame_cfg.seq_size == 16
        assert frame_cfg.checksum_size == 8

    def test_link_config_rejects_invalid_crc_generator(self):
        manager = ConfigManager(link=LinkConfig(
                checksum_cfg=ChecksumConfig.from_crc(CRCConfig(generator=[1, 1, 0]))
            )
        )
        with pytest.raises(ValueError, match='Generator must end with 1'):
            manager.link_layer_cfg.build_checksum()
