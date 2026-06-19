from src.physical_layer.channel_codes.channel_codes import RepetitionChannelCode
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config import PhysicalConfig
from src.system_configurations.config_manager import ConfigManager
from tests.utilities.dummies import DummyInterface


def test_physical_has_channel_code_config():
    cfg_manager = ConfigManager(top_layer='physical',
        physical=PhysicalConfig(
            channel_code=RepetitionChannelCode,
            code_params={'repetition': 3}
        )
    )
    stack = ProtocolStack(cfg_manager)
    physical_layer = stack.bottom_layer
    assert type(physical_layer.channel_code) is RepetitionChannelCode
    assert physical_layer.channel_code.r == 3

def test_stack_transmits_through_layers(link_stack):
    interface = DummyInterface()
    link_stack.transmit("sol", interface, src_mac='02:00:00:00:00:01', dst_mac='02:00:00:00:00:02')
    assert interface.last_sent_bits is not None

