import pytest

from src.link_layer.checksum import ParityChecksum
from src.link_layer.link import Link
from src.errors import LinkError

class DummyChannel:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = 0

    def transmit(self, bits):
        out = self.outputs[self.calls]
        self.calls += 1
        return out

@pytest.fixture
def bits():
    return "0101010101"

@pytest.fixture
def parity_checksum():
    return ParityChecksum()


def test_padding(parity_checksum):
    link = Link(channel=None, checksum=parity_checksum, block_size=4)
    padded, padding = link.pad_bits("10101")
    assert padded == "10101000"
    assert padding == 3

def test_unpadding(parity_checksum):
    link = Link(channel=None, checksum=parity_checksum, block_size=4)
    result = link.unpad_bits("10101000", 3)
    assert result == "10101"

def test_split_blocks(parity_checksum):
    link = Link(channel=None, checksum=parity_checksum, block_size=4)
    blocks = link.split_blocks("10101000")
    assert blocks == ["1010", "1000"]

def test_transmit_block_no_error(parity_checksum):
    channel = DummyChannel(["1010"])
    link = Link(channel, parity_checksum, block_size=4)
    result = link.transmit_block("1010")
    assert result == "1010"
    assert channel.calls == 1

def test_retry_success(parity_checksum):
    channel = DummyChannel([
        "1110",  # Wrong checksum
        "1010"  # Correct
    ])
    link = Link(channel, parity_checksum, block_size=4, max_retries=2)
    result = link.transmit_block("1010")
    assert result == "1010"
    assert channel.calls == 2

def test_complete_failure(parity_checksum):
    channel = DummyChannel([
        "1110",
        "1110",
        "1110"
    ])
    link = Link(channel, parity_checksum, block_size=4, max_retries=3)
    with pytest.raises(LinkError):
        link.transmit_block("1010")

def test_multiple_blocks(parity_checksum):
    channel = DummyChannel([
        "1010",  # block 1 ok
        "1100"  # block 2 ok
    ])
    link = Link(channel, parity_checksum, block_size=4)
    result = link.transmit("10101100")
    assert result == "10101100"

def test_block_independence(parity_checksum):
    channel = DummyChannel([
        "1110", "1010",  # block 1 fail → retry
        "1100"  # block 2 ok
    ])
    link = Link(channel, parity_checksum, block_size=4, max_retries=2)
    result = link.transmit("10101100")
    assert result == "10101100"
