import numpy as np
import pytest

from src.link_layer.checksum import ParityChecksum
from src.link_layer.frame import Frame
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

def build_link_and_frame(parity_checksum):
    payload = np.array([1, 1, 0, 1], dtype=np.uint8)
    seq = np.array([0, 0], dtype=np.uint8)
    checksum = np.array([1, 0], dtype=np.uint8)

    frame = Frame(payload, seq=0, checksum=checksum)

    return payload, seq, checksum, frame

def run_retry_test(parity_checksum, corrupted_bits, correct_bits):
    physical_layer = DummyPhysicalLayer([corrupted_bits, correct_bits])

    link = Link(
        physical_layer,
        parity_checksum,
        payload_size=4,
        seq_size=2,
        checksum_size=2,
        max_retries=2
    )
    payload = correct_bits[2:6]
    frame = Frame(payload, seq=0, checksum=correct_bits[6:])
    received_frame = link.transmit_frame(frame)

    assert received_frame.get_seq() == frame.get_seq()
    assert np.array_equal(received_frame.get_payload(), payload)
    assert physical_layer.calls == 2


@pytest.fixture
def bits():
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

    body_1 = [0, 0, 0, 1, 0, 1]
    body_2 = [0, 1, 0, 1, 0, 1]
    assert np.all(frames[0].get_payload() == [0, 1, 0, 1])
    assert frames[0].get_seq() == 0
    assert np.all(frames[0].get_checksum()[0] == parity_checksum.compute(body_1)[0])
    assert np.all(frames[1].get_payload() == [0, 1, 0, 1])
    assert frames[1].get_seq() == 1
    assert np.all(frames[1].get_checksum()[0] == parity_checksum.compute(body_2)[0])

def test_build_a_single_frame(parity_checksum):
    link = Link(None, checksum=parity_checksum, payload_size=8)
    bits = np.tile([0, 1], 4)
    frames = link.build_frames(bits)
    assert np.all(frames[0].get_payload() == bits)

def test_serialize_frame(parity_checksum):
    link = Link(None, checksum=parity_checksum, seq_size=2, payload_size=4)
    expected = np.array([0, 0, 1, 1, 1, 1, 0, 0], dtype=np.uint8)
    frame = Frame([1, 1, 1, 1], 0, [0, 0])
    serialized = link._serialize_frame(frame)
    assert np.all(serialized == expected)

def test_deserialize_frame(parity_checksum):
    link = Link(None, checksum=parity_checksum, seq_size=2, payload_size=4, checksum_size=2)
    serialized = np.array([0, 0, 1, 1, 1, 1, 0, 0], dtype=np.uint8)
    payload = [1, 1, 1, 1]
    checksum = [0, 0]
    deserialized = link._deserialize_frame(serialized)
    assert deserialized.get_seq() == 0
    assert np.all(deserialized.get_payload() == payload)
    assert np.all(deserialized.get_checksum() == checksum)

def test_transmit_frame_no_error(parity_checksum):
    seq = np.zeros(8, dtype=np.uint8)
    payload = np.array([1, 0, 1, 0], dtype=np.uint8)
    checksum = np.array([0, 0, 0, 0], dtype=np.uint8)
    transmitted_bits = np.concatenate((seq, payload, checksum))
    physical_layer = DummyPhysicalLayer([transmitted_bits])
    link = Link(physical_layer, parity_checksum, payload_size=4)
    frame = Frame(payload, 0, checksum)
    transmitted_frame = link.transmit_frame(frame)
    transmitted_payload = np.array([1, 0, 1, 0], dtype=np.uint8)
    transmitted_checksum = np.array([0, 0, 0, 0], dtype=np.uint8)
    transmitted_seq = 0
    assert transmitted_seq == transmitted_frame.get_seq()
    assert np.all(transmitted_payload == transmitted_frame.get_payload())
    assert np.all(transmitted_checksum == transmitted_frame.get_checksum())
    assert physical_layer.calls == 1

def test_payload_error_retry_success(parity_checksum):
    payload, seq, checksum, frame = build_link_and_frame(parity_checksum)
    corrupted_payload = payload.copy()
    corrupted_payload[2] ^= 1
    corrupted_bits = np.concatenate((seq, corrupted_payload, checksum))
    correct_bits = np.concatenate((seq, payload, checksum))

    run_retry_test(parity_checksum, corrupted_bits, correct_bits)

def test_seq_error_retry_success(parity_checksum):
    payload, seq, checksum, frame = build_link_and_frame(parity_checksum)

    corrupted_seq = seq.copy()
    corrupted_seq[1] ^= 1

    corrupted_bits = np.concatenate((corrupted_seq, payload, checksum))
    correct_bits = np.concatenate((seq, payload, checksum))

    run_retry_test(parity_checksum, corrupted_bits, correct_bits)

def test_complete_failure(parity_checksum):
    seq = np.zeros(2, dtype=np.uint8)
    payload = np.array([1, 1, 1, 0], dtype=np.uint8)
    checksum = np.array([0, 0], dtype=np.uint8)
    transmitted_bits = np.concatenate((seq, payload, checksum))
    physical_layer = DummyPhysicalLayer([transmitted_bits, transmitted_bits, transmitted_bits])
    link = Link(physical_layer, parity_checksum, payload_size=4, checksum_size=2, seq_size=2, max_retries=3)
    frame = Frame([0, 0, 0, 0], 0, checksum)
    with pytest.raises(LinkError):
        link.transmit_frame(frame)

def test_multiple_blocks(parity_checksum):
    payload = [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0]
    expected_frames = [
        [0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0],  # block 1 ok
        [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0]  # block 2 ok
    ]
    physical_layer = DummyPhysicalLayer(expected_frames)
    link = Link(physical_layer, parity_checksum, payload_size=8, seq_size=2, checksum_size=2, max_retries=3)
    result = link.transmit(payload)
    assert np.all(result == payload)

def test_block_independence(parity_checksum):
    payload = [1, 0, 1, 0, 1, 1, 0, 0]
    expected_frames = [
        [0, 0, 1, 1, 1, 0, 0, 0], [0, 0, 1, 0, 1, 0, 0, 0],  # block 1 fail → retry
        [0, 1, 1, 1, 0, 0, 0, 0]  # block 2 ok
    ]
    physical_layer = DummyPhysicalLayer(expected_frames)
    link = Link(physical_layer, parity_checksum, payload_size=4, seq_size=2, checksum_size=2, max_retries=2)
    result = link.transmit(payload)
    assert np.all(result == payload)
