from src.physical_layer.channel_codes.channel_codes import RepetitionChannelCode
from src.protocol_stack.protocol_stack import ProtocolStack
from src.system_configurations.config_manager import ConfigManager

class DummyInterface:
    def __init__(self):
        self.sent_bits = None

    def send(self, bits):
        self.sent_bits = bits

def test_link_has_checksum():
    from src.link_layer.checksum import ParityChecksum
    cfg_manager = ConfigManager(
        checksum=ParityChecksum,
        top_layer='link'
    )
    stack = ProtocolStack(cfg_manager)
    link = stack.top_layer
    assert type(link.checksum) is ParityChecksum

def test_physical_has_channel_code_config():
    cfg_manager = ConfigManager(
        top_layer='physical',
        channel_code=RepetitionChannelCode,
        repetition=3
    )
    stack = ProtocolStack(cfg_manager)
    physical_layer = stack.bottom_layer
    assert type(physical_layer.channel_code) is RepetitionChannelCode
    assert physical_layer.channel_code.r == 3

def test_stack_transmits_through_layers(link_stack):
    interface = DummyInterface()
    link_layer = link_stack.top_layer
    physical = link_layer.lower_layer

    def transmit_with_ack(bits, iface=None):
        interface.sent_bits = bits
        frame = link_layer._deserialize_frame(bits)
        ack = link_layer._build_ack(frame.get_seq())
        ack_bits = link_layer._serialize_frame(ack)
        link_layer.on_receive(ack_bits)

    physical.transmit = transmit_with_ack
    link_layer._validate_checksum = lambda x: True

    link_stack.transmit("sol", interface)
    assert interface.sent_bits is not None
