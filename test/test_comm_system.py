import pytest

from src.communications_system.comm_system import CommSystem
from src.physical_layer.alphabets.alphabets import AlphabetProvider
from src.physical_layer.codebook import Codebook
from src.physical_layer.codes.channel_codes import RepetitionChannelCode
from src.physical_layer.physical_layer import PhysicalLayer
from src.system_configurations.config_manager import ConfigManager

@pytest.fixture
def alphabet():
    return AlphabetProvider.provide_alphabet('test_16bits_alph')

@pytest.fixture
def message():
    return "sol mar luz bosque"

class TestCommSystemPhysicalLayer:

    def test_comm_system_no_noise(self, alphabet, message):
        cfg_manager = ConfigManager(error_prob=0.0, top_layer='physical')
        system = CommSystem(cfg_manager)
        codebook = Codebook(alphabet)
        received = system.transmit(codebook, message)
        assert received == message

    def test_build_stack_physical_layer(self):
        cfg_manager = ConfigManager(top_layer='physical')
        system = CommSystem(cfg_manager)
        assert isinstance(system.stack, PhysicalLayer)

    def test_channel_configuration(self):
        from src.physical_layer.codes.channel_codes import NoChannelCode
        cfg_manager = ConfigManager(
            error_prob=0.2,
            channel_code=NoChannelCode,
            top_layer='physical'
        )
        system = CommSystem(cfg_manager)
        channel_code = system.stack.channel_code
        channel = system.stack.channel

        assert channel.error_prob == 0.2
        assert isinstance(channel_code, NoChannelCode)


class TestCommSystemLinkLayer:

    def test_comm_system_no_noise(self, alphabet, message):
        cfg_manager = ConfigManager(error_prob=0.0, top_layer='link')
        system = CommSystem(cfg_manager)
        codebook = Codebook(alphabet)
        received = system.transmit(codebook, message)
        assert received == message

    def test_comm_system_with_noise_and_retries(self, alphabet, message):
        cfg_manager = ConfigManager(
            error_prob=0.1,
            channel_code=RepetitionChannelCode,
            repetition=3,
            max_retries=50,
            top_layer = 'link'
        )
        system = CommSystem(cfg_manager)
        codebook = Codebook(alphabet)
        received = system.transmit(codebook, message)
        assert received == message

    def test_build_stack_link_layer(self):
        cfg_manager = ConfigManager(top_layer='link')
        system = CommSystem(cfg_manager)
        from src.link_layer.link import Link
        assert isinstance(system.stack, Link)
        assert isinstance(system.stack.lower_layer, PhysicalLayer)

    def test_stack_order_is_correct(self):
        cfg_manager = ConfigManager(top_layer='link')
        system = CommSystem(cfg_manager)
        link = system.stack
        physical = link.lower_layer

        assert physical.lower_layer is None

    def test_link_has_checksum(self):
        from src.link_layer.checksum import ParityChecksum
        cfg_manager = ConfigManager(
            checksum=ParityChecksum,
            top_layer='link'
        )
        system = CommSystem(cfg_manager)
        link = system.stack
        assert isinstance(link.checksum, ParityChecksum)
