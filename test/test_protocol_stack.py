import pytest

from src.link_layer.link_layer import LinkLayer
from src.physical_layer.codebook import Codebook
from src.physical_layer.codes.channel_codes import RepetitionChannelCode
from src.physical_layer.physical_layer import PhysicalLayer
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config_manager import ConfigManager

@pytest.fixture
def message():
    return "sol mar luz bosque"

class TestProtocolStackPhysicalLayer:

    def test_stack_no_noise(self, message):
        cfg_manager = ConfigManager(error_prob=0.0, top_layer='physical')
        stack = ProtocolStack(cfg_manager)
        received = stack.transmit(message)
        assert received == message

    def test_build_stack_physical_layer(self):
        cfg_manager = ConfigManager(top_layer='physical')
        stack = ProtocolStack(cfg_manager)
        assert isinstance(stack.top_layer, PhysicalLayer)

    def test_channel_configuration(self):
        from src.physical_layer.codes.channel_codes import NoChannelCode
        cfg_manager = ConfigManager(
            error_prob=0.2,
            channel_code=NoChannelCode,
            top_layer='physical'
        )
        stack = ProtocolStack(cfg_manager)
        channel_code = stack.top_layer.channel_code
        channel = stack.top_layer.channel

        assert channel.error_prob == 0.2
        assert isinstance(channel_code, NoChannelCode)


class TestProtocolStackLinkLayer:

    def test_stack_no_noise(self, message):
        cfg_manager = ConfigManager(error_prob=0.0, top_layer='link')
        stack = ProtocolStack(cfg_manager)
        received = stack.transmit(message)
        assert received == message

    def test_stack_with_noise_and_retries(self, message):
        cfg_manager = ConfigManager(
            error_prob=0.1,
            channel_code=RepetitionChannelCode,
            repetition=9,
            max_retries=50,
            top_layer = 'link'
        )
        stack = ProtocolStack(cfg_manager)
        received = stack.transmit(message)
        assert received == message

    def test_build_stack_link_layer(self):
        cfg_manager = ConfigManager(top_layer='link')
        stack = ProtocolStack(cfg_manager)
        assert isinstance(stack.top_layer, LinkLayer)
        assert isinstance(stack.top_layer.lower_layer, PhysicalLayer)

    def test_stack_order_is_correct(self):
        cfg_manager = ConfigManager(top_layer='link')
        stack = ProtocolStack(cfg_manager)
        link_layer = stack.top_layer
        physical = link_layer.lower_layer

        assert physical.lower_layer is None

    def test_link_has_checksum(self):
        from src.link_layer.checksum import ParityChecksum
        cfg_manager = ConfigManager(
            checksum=ParityChecksum,
            top_layer='link'
        )
        stack = ProtocolStack(cfg_manager)
        link = stack.top_layer
        assert isinstance(link.checksum, ParityChecksum)
