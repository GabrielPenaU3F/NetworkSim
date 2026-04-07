import pytest

from src.link_layer.checksum import ParityChecksum, CRCChecksum
from src.infrastructure.channels import BinarySymmetricChannel
from src.physical_layer.channel_codes.channel_codes import NoChannelCode
from src.system_configurations.config_manager import ConfigManager

@pytest.fixture
def cfg_manager():
    return ConfigManager()

def test_unknown_parameter_raises_error():
    with pytest.raises(KeyError):
        ConfigManager(apple=2)

class TestInfrastructureConfig:

    def test_default_alphabet_is_the_test_alphpabet(self, cfg_manager):
        infra_cfg = cfg_manager.get_infrastructure_config()
        assert infra_cfg.alphabet == 'test_16bits_alph'

    def test_infrastructure_config_defaults(self, cfg_manager):
        infra_cfg = cfg_manager.get_infrastructure_config()
        assert infra_cfg.channel_cls is BinarySymmetricChannel
        assert infra_cfg.channel_params['error_prob'] == 0.05

    def test_infrastructure_config_override(self):
        manager = ConfigManager(error_prob=0.2)
        infra_cfg = manager.get_infrastructure_config()
        assert infra_cfg.channel_params['error_prob'] == 0.2


class TestProtocolStackConfig:

    def test_default_top_layer_is_link(self, cfg_manager):
        stack_cfg = cfg_manager.get_protocol_stack_config()
        assert stack_cfg.top_layer == 'link'

class TestPhysicalLayerConfig:

    def test_physical_config_defaults(self, cfg_manager):
        phys = cfg_manager.get_physical_layer_config()
        assert phys.code_cls is NoChannelCode

    def test_physical_config_override_does_not_affect_other_parameters(self):
        manager = ConfigManager(error_prob=0.2)
        phys = manager.get_physical_layer_config()
        assert phys.code_cls is NoChannelCode


class TestLinkLayerConfig:

    def test_link_config_defaults(self, cfg_manager):
        link = cfg_manager.get_link_layer_config()
        assert link.max_retries == 5

    def test_frame_config_defaults(self, cfg_manager):
        frame_cfg = cfg_manager.get_link_layer_config().frame_config
        assert frame_cfg.payload_size == 8
        assert frame_cfg.seq_size == 8
        assert frame_cfg.checksum_size == 4

    def test_link_config_checksum_defaults(self, cfg_manager):
        link = cfg_manager.get_link_layer_config()
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
