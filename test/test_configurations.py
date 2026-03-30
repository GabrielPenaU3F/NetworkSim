import pytest

from src.link_layer.checksum import ParityChecksum, CRCChecksum
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode
from src.system_configurations.config_manager import ConfigManager

def test_unknown_parameter_raises_error():
    with pytest.raises(KeyError):
        ConfigManager(apple=2)

class TestPhysicalLayerConfig:

    def test_physical_config_defaults(self):
        cfg = ConfigManager()
        phys = cfg.get_physical_layer_config()
        assert phys.channel_cls is BinarySymmetricChannel
        assert phys.channel_params['error_prob'] == 0.05
        assert phys.code_cls is NoChannelCode

    def test_physical_config_override(self):
        manager = ConfigManager(error_prob=0.2)
        phys = manager.get_physical_layer_config()
        assert phys.channel_params['error_prob'] == 0.2

    def test_physical_config_override_does_not_affect_other_parameters(self):
        manager = ConfigManager(error_prob=0.2)
        phys = manager.get_physical_layer_config()
        assert phys.channel_cls is BinarySymmetricChannel
        assert phys.code_cls is NoChannelCode


class TestLinkLayerConfig:

    def test_link_config_defaults(self):
        cfg = ConfigManager()
        link = cfg.get_link_layer_config()
        assert link.max_retries == 5

    def test_frame_config_defaults(self):
        cfg = ConfigManager()
        frame_cfg = cfg.get_link_layer_config().frame_config
        assert frame_cfg.payload_size == 8
        assert frame_cfg.seq_size == 8
        assert frame_cfg.checksum_size == 4

    def test_link_config_checksum_defaults(self):
        cfg = ConfigManager()
        link = cfg.get_link_layer_config()
        assert link.checksum_cls is ParityChecksum
        assert link.checksum_params == {}

    def test_link_config_override(self):
        manager = ConfigManager(max_retries=10, checksum=CRCChecksum, crc_generator=[1, 0, 0, 1])
        link = manager.get_link_layer_config()
        assert link.max_retries == 10
        assert link.checksum_cls is CRCChecksum
        assert link.checksum_params['crc_generator'] == [1, 0, 0, 1]

    def test_physical_config_override_does_not_affect_other_parameters(self):
        manager = ConfigManager(payload_size=16, seq_size=16, checksum_size=8)
        link = manager.get_link_layer_config()
        assert link.checksum_cls is ParityChecksum
        assert link.frame_config.payload_size == 16
        assert link.frame_config.seq_size == 16
        assert link.frame_config.checksum_size == 8
