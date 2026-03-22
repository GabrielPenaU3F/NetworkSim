import pytest

from src.comm_system import CommSystem
from src.config import Config
from src.errors import LinkError
from src.physical_layer.alphabets.alphabets import AlphabetProvider
from src.physical_layer.codebook import Codebook
from src.physical_layer.codes.channel_codes import RepetitionChannelCode


@pytest.fixture
def alphabet():
    return AlphabetProvider.provide_alphabet('test_16bits_alph')

@pytest.fixture
def message():
    return "sol mar luz bosque"

def test_comm_system_no_noise(alphabet, message):
    config = Config(error_prob=0.0)
    system = CommSystem(config)
    codebook = Codebook(alphabet)
    received = system.transmit(codebook, message)
    assert received == message

def test_comm_system_with_noise_and_retries(alphabet, message):
    config = Config(
        error_prob=0.1,
        channel_code=RepetitionChannelCode,
        max_retries=50
    )
    system = CommSystem(config)
    codebook = Codebook(alphabet)
    received = system.transmit(codebook, message)
    assert received == message
