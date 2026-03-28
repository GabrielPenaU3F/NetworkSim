import numpy as np
import pytest

from src.link_layer.checksum import ParityChecksum
from src.link_layer.link import Link, pad_bits, unpad_bits
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


def test_padding():
    padded, padding = pad_bits([1, 0, 1, 0, 1], 4)
    assert np.all(padded == [1, 0, 1, 0, 1, 0, 0, 0])
    assert padding == 3

def test_unpadding():
    result = unpad_bits([1, 0, 1, 0, 1, 0, 0, 0], 3)
    assert np.all(result == [1, 0, 1, 0, 1])

def test_compute_checksum_parity(parity_checksum):
    link = Link(None, parity_checksum, checksum_size=4)
    bits = [1, 0, 1, 1]
    raw_cs = parity_checksum.compute(bits)
    expected_cs = np.concatenate((raw_cs, np.zeros(3)))
    actual_cs = link._compute_checksum(raw_cs)
    assert np.all(actual_cs == expected_cs)


def test_build_frames(parity_checksum):
    link = Link(None, checksum=parity_checksum, payload_size=4)
    bits = np.tile([0, 1], 4)
    frames = link.build_frames(bits)
    assert len(frames) == 2
    assert np.all(frames[0].get_payload() == [0, 1, 0, 1])
    assert frames[0].get_seq() == 0
    assert np.all(frames[1].get_payload() == [0, 1, 0, 1])
    assert frames[1].get_seq() == 1

def test_build_a_single_frame(parity_checksum):
    link = Link(None, checksum=parity_checksum, payload_size=8)
    bits = np.tile([0, 1], 4)
    frames = link.build_frames(bits)
    assert np.all(frames[0].get_payload() == bits)

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
