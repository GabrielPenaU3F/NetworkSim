import numpy as np
import pytest
from numpy.random import Generator

from src.communications_system.layer_hub import LayerHub
from src.link_layer.checksum import CRCChecksum
from src.link_layer.link import Link
from src.physical_layer.channels import BinarySymmetricChannel
from src.physical_layer.codes.channel_codes import NoChannelCode
from src.physical_layer.physical_layer import PhysicalLayer
from src.system_configurations.config import PhysicalConfig, LinkConfig, FrameConfig


@pytest.fixture
def dummy_physical_layer():
    return PhysicalLayer(BinarySymmetricChannel, NoChannelCode)

@pytest.fixture
def link_config_fixture():
    return LinkConfig(
            max_retries=5,
            frame_config=FrameConfig(payload_size=8, seq_size=4, checksum_size=4),
            checksum_cls=CRCChecksum,
            checksum_params={}
        )

class TestPhysicalLayerBuilder:

    def test_build_physical_layer_basic(self):
        config = PhysicalConfig(
            channel_cls=BinarySymmetricChannel,
            channel_params={'error_prob': None, 'channel_rng': None},
            code_cls=NoChannelCode,
            code_params={}
        )
        layer = LayerHub.build_physical_layer(config)
        assert isinstance(layer, PhysicalLayer)
        assert isinstance(layer.channel, BinarySymmetricChannel)
        assert isinstance(layer.channel_code, NoChannelCode)

    def test_build_physical_layer_channel_params(self):
        p = 0.3
        rng = np.random.default_rng(0)
        config = PhysicalConfig(
            channel_cls=BinarySymmetricChannel,
            channel_params={'error_prob': p, 'channel_rng': rng},
            code_cls=NoChannelCode,
            code_params={}
        )
        layer = LayerHub.build_physical_layer(config)
        assert layer.channel.error_prob == p
        assert isinstance(layer.channel.rng, Generator)


class TestLinkLayerBuilder:

    def test_build_link_layer_basic(self, dummy_physical_layer, link_config_fixture):
        layer = LayerHub.build_link_layer(link_config_fixture, dummy_physical_layer)
        assert isinstance(layer, Link)
        assert isinstance(layer.lower_layer, PhysicalLayer)
        assert isinstance(layer.checksum, CRCChecksum)

    def test_build_link_layer_frame_params(self, dummy_physical_layer, link_config_fixture):
        layer = LayerHub.build_link_layer(link_config_fixture, dummy_physical_layer)
        assert isinstance(layer, Link)
        assert isinstance(layer.lower_layer, PhysicalLayer)
        assert isinstance(layer.checksum, CRCChecksum)