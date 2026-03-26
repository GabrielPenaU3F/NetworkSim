import numpy as np
import pytest

from src.link_layer.checksum import ParityChecksum
from src.link_layer.link import Link
from src.errors import LinkError

class DummyPhysicalLayer:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = 0

    def transmit(self, bits):
        out = self.outputs[self.calls]
        self.calls += 1
        return out

@pytest.fixture
def bits():
    return np.tile([0, 1], 5)

@pytest.fixture
def bits_2():
    return np.array([1, 0, 1, 0, 1, 1, 0, 0])

@pytest.fixture
def parity_checksum():
    return ParityChecksum()


def test_padding(parity_checksum):
    link = Link(None, checksum=parity_checksum, payload_size=4)
    padded, padding = link.pad_bits([1, 0, 1, 0, 1])
    assert np.all(padded == [1, 0, 1, 0, 1, 0, 0, 0])
    assert padding == 3

def test_unpadding(parity_checksum):
    link = Link(None, checksum=parity_checksum, payload_size=4)
    result = link.unpad_bits([1, 0, 1, 0, 1, 0, 0, 0], 3)
    assert np.all(result == [1, 0, 1, 0, 1])

def test_split_blocks(parity_checksum):
    link = Link(None, checksum=parity_checksum, payload_size=4)
    blocks = link.split_blocks([1, 0, 1, 0, 1, 0, 0, 0])
    assert np.all(blocks == [[1, 0, 1, 0], [1, 0, 0, 0]])

def test_transmit_block_no_error(parity_checksum):
    blocks = [[1, 0, 1, 0]] # A single block
    physical_layer = DummyPhysicalLayer(blocks)
    link = Link(physical_layer, parity_checksum, payload_size=4)
    result = link.transmit_frame(blocks)
    assert np.all(result == [1, 0, 1, 0])
    assert physical_layer.calls == 1

def test_retry_success(parity_checksum):
    blocks = [
        [1, 1, 1, 0],  # Wrong checksum
        [1, 0, 1, 0]  # Correct
    ]
    physical_layer = DummyPhysicalLayer(blocks)
    link = Link(physical_layer, parity_checksum, payload_size=4, max_retries=2)
    result = link.transmit_frame([1, 0, 1, 0])
    assert np.all(result == [1, 0, 1, 0])
    assert physical_layer.calls == 2

def test_complete_failure(parity_checksum):
    blocks = [
        [1, 1, 1, 0],
        [1, 1, 1, 0],
        [1, 1, 1, 0]
    ]
    physical_layer = DummyPhysicalLayer(blocks)
    link = Link(physical_layer, parity_checksum, payload_size=4, max_retries=3)
    with pytest.raises(LinkError):
        link.transmit_frame([1, 0, 1, 0])

def test_multiple_blocks(parity_checksum, bits_2):
    blocks = [
        [1, 0, 1, 0],  # block 1 ok
        [1, 1, 0, 0]  # block 2 ok
    ]
    physical_layer = DummyPhysicalLayer(blocks)
    link = Link(physical_layer, parity_checksum, payload_size=4)
    result = link.transmit(bits_2)
    assert np.all(result == bits_2)

def test_block_independence(parity_checksum, bits_2):
    blocks = [
        [1, 1, 1, 0], [1, 0, 1, 0],  # block 1 fail → retry
        [1, 1, 0, 0]  # block 2 ok
    ]
    physical_layer = DummyPhysicalLayer(blocks)
    link = Link(physical_layer, parity_checksum, payload_size=4, max_retries=2)
    result = link.transmit(bits_2)
    assert np.all(result == bits_2)
