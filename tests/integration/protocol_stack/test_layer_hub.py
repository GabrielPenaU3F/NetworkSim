import numpy as np

from src.link_layer.checksum import CRCChecksum
from src.link_layer.link_layer import LinkLayer
from src.physical_layer.channel_codes.channel_codes import NoChannelCode, HammingChannelCode
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.layer_hub import LayerHub
from src.system_configurations.config_manager import ConfigManager

class TestPhysicalLayerBuilder:

    def test_builds_physical_layer_instance(self):
        config = ConfigManager(top_layer='physical', channel_code=NoChannelCode)
        layer = LayerHub.build_physical_layer(config)
        assert type(layer) is PhysicalLayer

    def test_physical_layer_has_correct_channel_code(self):
        config = ConfigManager(top_layer='physical', channel_code=NoChannelCode)
        layer = LayerHub.build_physical_layer(config)
        assert type(layer.channel_code) is NoChannelCode

    def test_physical_layer_channel_code_follows_config(self):
        config = ConfigManager(top_layer='physical', channel_code=HammingChannelCode)
        layer = LayerHub.build_physical_layer(config)
        assert type(layer.channel_code) is HammingChannelCode


class TestLinkLayerBuilder:

    def test_builds_link_layer_instance(self):
        config = ConfigManager(top_layer='link')
        layer = LayerHub.build_link_layer(config)
        assert type(layer) is LinkLayer

    def test_link_layer_has_correct_checksum(self):
        config = ConfigManager(top_layer='link', checksum=CRCChecksum, crc_generator=[1, 0, 0, 1])
        layer = LayerHub.build_link_layer(config)
        assert type(layer.checksum) is CRCChecksum
        assert np.all(layer.checksum.generator == [1, 0, 0, 1])

    def test_link_layer_has_correct_max_retries(self):
        config = ConfigManager(top_layer='link', max_retries=10)
        layer = LayerHub.build_link_layer(config)
        assert layer.max_retries == 10

    def test_link_layer_has_correct_payload_size(self):
        config = ConfigManager(top_layer='link', payload_size=16)
        layer = LayerHub.build_link_layer(config)
        assert layer.payload_size == 16

    def test_link_layer_has_correct_seq_size(self):
        config = ConfigManager(top_layer='link', seq_size=4)
        layer = LayerHub.build_link_layer(config)
        assert layer.seq_size == 4
