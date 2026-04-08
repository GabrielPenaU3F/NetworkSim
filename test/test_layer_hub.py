import numpy as np
import pytest
from numpy.random import Generator

from src.link_layer.checksum import CRCChecksum
from src.link_layer.link_layer import LinkLayer
from src.infrastructure.channels import BinarySymmetricChannel
from src.physical_layer.channel_codes.channel_codes import NoChannelCode, HammingChannelCode
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.layer_hub import LayerHub
from src.system_configurations.config_manager import ConfigManager


@pytest.fixture
def config_manager():
    return ConfigManager(
            error_prob=0,
            channel_code=NoChannelCode,
            max_retries=5,
            payload_size=8, seq_size=4, checksum_size=4,
            checksum=CRCChecksum
        )

class TestPhysicalLayerBuilder:

    def test_build_physical_layer_default(self, config_manager):
        layer = LayerHub.build_physical_layer(config_manager)
        assert isinstance(layer, PhysicalLayer)
        assert isinstance(layer.channel_code, NoChannelCode)

    def test_build_physical_layer_channel_params(self):
        config=ConfigManager(
            channel_code=HammingChannelCode,
        )
        layer = LayerHub.build_physical_layer(config)
        assert isinstance(layer.channel_code, HammingChannelCode)


class TestLinkLayerBuilder:

    def test_build_link_layer_basic(self, config_manager):
        layer = LayerHub.build_link_layer(config_manager)
        assert isinstance(layer, LinkLayer)
        assert isinstance(layer.lower_layer, PhysicalLayer)
        assert isinstance(layer.checksum, CRCChecksum)

    def test_build_link_layer_frame_params(self, config_manager):
        layer = LayerHub.build_link_layer(config_manager)
        assert isinstance(layer, LinkLayer)
        assert isinstance(layer.lower_layer, PhysicalLayer)
        assert isinstance(layer.checksum, CRCChecksum)
