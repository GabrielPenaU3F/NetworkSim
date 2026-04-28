import numpy as np
import pytest

from src.link_layer.checksum import ParityChecksum
from src.link_layer.frame import Frame
from src.link_layer.link_layer import LinkLayer
from src.protocol_stack.layer_hub import LayerHub
from src.utils import pad_bits


class DummyLowerLayer:
    def __init__(self):
        self.upper_layer = None
        self.sent_bits = []
        self.calls = 0

    def attach_upper(self, upper):
        self.upper_layer = upper

    def transmit(self, bits, interface=None):
        self.sent_bits.append(bits)
        self.calls += 1

# def build_link_and_frame():
#     payload = np.array([1, 1, 0, 1], dtype=np.uint8)
#     seq = np.array([0, 0], dtype=np.uint8)
#     checksum = np.array([1, 0], dtype=np.uint8)
#     frame = Frame(payload, seq=0, checksum=checksum)
#     return payload, seq, checksum, frame

@pytest.fixture
def bits():
    return np.array([1, 0, 1, 0, 1, 1, 0, 0])

@pytest.fixture
def tile_bits():
    def _make_tile(n):
        return np.tile([0, 1], n)
    return _make_tile

@pytest.fixture
def dummy_physical():
    return DummyLowerLayer()

@pytest.fixture
def testing_link_layer():
    dummy_physical = DummyLowerLayer()
    checksum = ParityChecksum()
    link_layer = LinkLayer(checksum, seq_size=2, payload_size=8, checksum_size=2)
    LayerHub._connect_layers(link_layer, dummy_physical)
    return link_layer

@pytest.fixture
def frame_to_serialize():
    def _make(is_last=1):
        bits = np.tile([0, 1], 2)
        padded_bits, _ = pad_bits(bits, 8)
        frame = Frame(seq=0, is_last=is_last, real_length=4, payload=padded_bits, checksum=[0, 0])
        return frame
    return _make

@pytest.fixture
def serialized_bits():
    def _make(is_last):
        serialized = np.array([
            0, 0,  # seq
            is_last,  # is_last
            0, 1, 0, 0,  # real_length = 4
            0, 1, 0, 1, 0, 0, 0, 0,  # payload (0101 + padding)
            0, 0  # checksum
        ], dtype=np.uint8)
        return serialized
    return _make

@pytest.fixture
def base_body():
    base_body = np.array([
        0, 0,  # seq (2 bits)
        1,  # is_last
        0, 1, 0, 0,  # real_length = 4
        0, 1, 0, 1, 0, 0, 0, 0  # payload (padded)
    ], dtype=np.uint8)
    return base_body


class TestSerialization:

    def test_serialize_frame_seq(self, testing_link_layer, frame_to_serialize):
        expected_seq = np.array([0, 0], dtype=np.uint8)
        serialized = testing_link_layer._serialize_frame(frame_to_serialize(is_last=1))
        seq_end = testing_link_layer.seq_size
        actual_seq = serialized[:seq_end]
        assert np.all(actual_seq == expected_seq)

    def test_serialize_frame_is_last(self, testing_link_layer, frame_to_serialize):
        serialized = testing_link_layer._serialize_frame(frame_to_serialize(is_last=1))
        seq_end = testing_link_layer.seq_size
        actual_is_last = serialized[seq_end]
        assert actual_is_last == 1

    def test_serialize_frame_is_not_last(self, testing_link_layer, frame_to_serialize):
        serialized = testing_link_layer._serialize_frame(frame_to_serialize(is_last=0))
        seq_end = testing_link_layer.seq_size
        actual_is_last = serialized[seq_end]
        assert actual_is_last == 0

    def test_serialize_frame_real_length(self, testing_link_layer, frame_to_serialize):
        # Size is ceil(log2(1 + payload_size)), thus, 4 binary digits. So 4 in binary (with four digits) is 0100
        expected_real_length = np.array([0, 1, 0, 0], dtype=np.uint8)
        serialized = testing_link_layer._serialize_frame(frame_to_serialize(is_last=1))
        real_length_start = 1 + testing_link_layer.seq_size
        real_length_end = real_length_start + testing_link_layer.payload_length_field_size
        actual_real_length = serialized[real_length_start: real_length_end]
        assert np.all(actual_real_length == expected_real_length)

    def test_serialize_frame_payload(self, testing_link_layer, frame_to_serialize):
        frame = frame_to_serialize(is_last=1)
        serialized = testing_link_layer._serialize_frame(frame)
        payload_start = testing_link_layer.seq_size + 1 + testing_link_layer.payload_length_field_size
        payload_end = payload_start + testing_link_layer.payload_size
        expected_payload = frame.get_payload()
        actual_payload = serialized[payload_start: payload_end]
        assert np.all(actual_payload == expected_payload)

    def test_serialize_frame_checksum(self, testing_link_layer, frame_to_serialize):
        expected_checksum = np.array([0, 0], dtype=np.uint8)
        serialized = testing_link_layer._serialize_frame(frame_to_serialize(is_last=1))
        payload_start = testing_link_layer.seq_size + 1 + testing_link_layer.payload_length_field_size
        payload_end = payload_start + testing_link_layer.payload_size
        actual_checksum = serialized[payload_end:]
        assert np.all(actual_checksum == expected_checksum)


class TestDeserialization:

    def test_deserialize_frame_seq(self, testing_link_layer, serialized_bits):
        deserialized = testing_link_layer._deserialize_frame(serialized_bits(1))
        assert deserialized.get_seq() == 0

    def test_deserialize_frame_is_last(self, testing_link_layer, serialized_bits):
        deserialized = testing_link_layer._deserialize_frame(serialized_bits(1))
        assert deserialized.get_is_last() == 1

    def test_deserialize_frame_is_not_last(self, testing_link_layer, serialized_bits):
        deserialized = testing_link_layer._deserialize_frame(serialized_bits(0))
        assert deserialized.get_is_last() == 0

    def test_deserialize_frame_real_length(self, testing_link_layer, serialized_bits):
        deserialized = testing_link_layer._deserialize_frame(serialized_bits(1))
        assert deserialized.get_real_length() == 4

    def test_deserialize_frame_payload(self, testing_link_layer, serialized_bits):
        deserialized = testing_link_layer._deserialize_frame(serialized_bits(1))
        expected_payload = np.array([0, 1, 0, 1], dtype=np.uint8)
        assert np.all(deserialized.get_payload() == expected_payload)


class TestLinkLayer:

    def test_build_a_single_frame_header(self, testing_link_layer, tile_bits):
        bits = tile_bits(2)
        frames = testing_link_layer._build_frames(bits)
        frame = frames[0]

        assert frame.get_seq() == 0
        assert frame.get_is_last() == 1
        assert frame.get_real_length() == 4

    def test_build_a_single_frame_payload_without_padding(self, testing_link_layer, tile_bits):
        bits = tile_bits(4) # Exactly 8 bits on a link layer with payload_size=8
        frames = testing_link_layer._build_frames(bits)
        frame = frames[0]
        assert np.all(frame.get_payload() == bits)

    def test_build_a_single_frame_payload_with_padding(self, testing_link_layer, tile_bits):
        bits = tile_bits(2) # 4 bits on a link layer with payload_size=8, needs padding
        frames = testing_link_layer._build_frames(bits)
        frame = frames[0]
        expected_payload = np.concatenate(([0, 1, 0, 1], [0, 0, 0, 0]))
        assert np.all(frame.get_payload() == expected_payload)

    def test_build_frames(self, testing_link_layer, tile_bits):
        bits = tile_bits(7)
        frames = testing_link_layer._build_frames(bits)
        f0, f1 = frames

        # ------------------
        # Frame 0 (payload field is full)
        # ------------------
        expected_payload_0 = bits[:8]

        assert f0.get_seq() == 0
        assert f0.get_is_last() == 0
        assert f0.get_real_length() == 8
        assert np.all(f0.get_payload() == expected_payload_0)

        # ------------------
        # Frame 1 (with two-bit padding)
        # ------------------
        real_payload_1 = bits[8:]  # 6 bits
        expected_payload_1 = np.concatenate((real_payload_1, [0, 0]))

        assert f1.get_seq() == 1
        assert f1.get_is_last() == 1
        assert f1.get_real_length() == 6
        assert np.all(f1.get_payload() == expected_payload_1)

    def test_build_body_structure(self, testing_link_layer):
        seq = 0
        is_last = 1
        real_length = 4
        payload = np.array([0, 1, 0, 1, 0, 0, 0, 0], dtype=np.uint8)

        body = testing_link_layer._build_body(seq, is_last, real_length, payload)

        expected = np.array([
            0, 0,  # seq (2 bits)
            1,  # is_last
            0, 1, 0, 0,  # real_length = 4
            0, 1, 0, 1, 0, 0, 0, 0  # payload
        ], dtype=np.uint8)

        assert np.all(body == expected)

    def test_checksum_changes_with_seq(self, testing_link_layer, base_body):
        body_with_different_seq = base_body.copy()
        body_with_different_seq[0] ^= 1  # flip a bit from seq
        cs1 = testing_link_layer._compute_checksum(base_body)
        cs2 = testing_link_layer._compute_checksum(body_with_different_seq)

        assert not np.all(cs1 == cs2)

    def test_checksum_changes_with_is_last(self, testing_link_layer, base_body):
        body_with_islast_0 = base_body.copy()
        body_with_islast_0[2] ^= 1  # flip is_last
        cs1 = testing_link_layer._compute_checksum(base_body)
        cs2 = testing_link_layer._compute_checksum(body_with_islast_0)

        assert not np.all(cs1 == cs2)

    def test_checksum_changes_with_real_length(self, testing_link_layer, base_body):
        body_with_different_real_length = base_body.copy()
        body_with_different_real_length[3] ^= 1  # flip a bit from real_length
        cs1 = testing_link_layer._compute_checksum(base_body)
        cs2 = testing_link_layer._compute_checksum(body_with_different_real_length)

        assert not np.all(cs1 == cs2)

    def test_checksum_changes_with_payload(self, testing_link_layer, base_body):
        body_with_different_payload = base_body.copy()
        body_with_different_payload[-1] ^= 1  # flip last payload bit
        cs1 = testing_link_layer._compute_checksum(base_body)
        cs2 = testing_link_layer._compute_checksum(body_with_different_payload)

        assert not np.all(cs1 == cs2)


# TODO: messages are not being unpadded on rebuild. This needs to be tested and implemented

# def test_link_tx_serializes_and_sends_downwards(testing_link_layer):
#     bits = np.array([1,0,1,0,1,1,0,0], dtype=np.uint8)
#     testing_link_layer.transmit(bits)
#     physical = testing_link_layer.lower_layer
#     assert len(physical.sent_bits) > 0
#     assert physical.calls == 2
#
# def test_link_rx_deserializes(testing_link_layer):
#     frame_bits = np.array([0, 0, 1, 1, 1, 1, 1, 0, 0], dtype=np.uint8)
#     expected_payload = np.array([1, 1, 1, 1], dtype=np.uint8)
#     output = testing_link_layer.on_receive(frame_bits)
#     assert np.all(output == expected_payload)

# def test_transmit_frame_no_error(parity_checksum):
#     seq = np.zeros(8, dtype=np.uint8)
#     payload = np.array([1, 0, 1, 0], dtype=np.uint8)
#     checksum = np.array([0, 0, 0, 0], dtype=np.uint8)
#     transmitted_bits = np.concatenate((seq, payload, checksum))
#     physical_layer = DummyPhysicalLayer([transmitted_bits])
#     link = LinkLayer(physical_layer, parity_checksum, payload_size=4)
#     frame = Frame(payload, 0, checksum)
#     transmitted_frame = link.transmit_frame(frame)
#     transmitted_payload = np.array([1, 0, 1, 0], dtype=np.uint8)
#     transmitted_checksum = np.array([0, 0, 0, 0], dtype=np.uint8)
#     transmitted_seq = 0
#     assert transmitted_seq == transmitted_frame.get_seq()
#     assert np.all(transmitted_payload == transmitted_frame.get_payload())
#     assert np.all(transmitted_checksum == transmitted_frame.get_checksum())
#     assert physical_layer.calls == 1
#
# def test_run_retry(parity_checksum, corrupted_bits, correct_bits):
#     physical_layer = DummyPhysicalLayer([corrupted_bits, correct_bits])
#
#     link = LinkLayer(
#         physical_layer,
#         parity_checksum,
#         payload_size=4,
#         seq_size=2,
#         checksum_size=2,
#         max_retries=2
#     )
#     payload = correct_bits[2:6]
#     frame = Frame(payload, seq=0, checksum=correct_bits[6:])
#     received_frame = link.transmit_frame(frame)
#
#     assert received_frame.get_seq() == frame.get_seq()
#     assert np.array_equal(received_frame.get_payload(), payload)
#     assert physical_layer.calls == 2

#
# def test_payload_error_retry_success(parity_checksum):
#     payload, seq, checksum, frame = build_link_and_frame(parity_checksum)
#     corrupted_payload = payload.copy()
#     corrupted_payload[2] ^= 1
#     corrupted_bits = np.concatenate((seq, corrupted_payload, checksum))
#     correct_bits = np.concatenate((seq, payload, checksum))
#
#     run_retry_test(parity_checksum, corrupted_bits, correct_bits)
#
# def test_seq_error_retry_success(parity_checksum):
#     payload, seq, checksum, frame = build_link_and_frame(parity_checksum)
#
#     corrupted_seq = seq.copy()
#     corrupted_seq[1] ^= 1
#
#     corrupted_bits = np.concatenate((corrupted_seq, payload, checksum))
#     correct_bits = np.concatenate((seq, payload, checksum))
#
#     run_retry_test(parity_checksum, corrupted_bits, correct_bits)
#
# def test_complete_failure(parity_checksum):
#     seq = np.zeros(2, dtype=np.uint8)
#     payload = np.array([1, 1, 1, 0], dtype=np.uint8)
#     checksum = np.array([0, 0], dtype=np.uint8)
#     transmitted_bits = np.concatenate((seq, payload, checksum))
#     physical_layer = DummyPhysicalLayer([transmitted_bits, transmitted_bits, transmitted_bits])
#     link = LinkLayer(physical_layer, parity_checksum, payload_size=4, checksum_size=2, seq_size=2, max_retries=3)
#     frame = Frame([0, 0, 0, 0], 0, checksum)
#     with pytest.raises(LinkError):
#         link.transmit_frame(frame)
#
# def test_multiple_blocks(parity_checksum):
#     payload = [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0]
#     expected_frames = [
#         [0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0],  # block 1 ok
#         [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0]  # block 2 ok
#     ]
#     physical_layer = DummyPhysicalLayer(expected_frames)
#     link = LinkLayer(physical_layer, parity_checksum, payload_size=8, seq_size=2, checksum_size=2, max_retries=3)
#     result = link.transmit(payload)
#     assert np.all(result == payload)
#
# def test_block_independence(parity_checksum):
#     payload = [1, 0, 1, 0, 1, 1, 0, 0]
#     expected_frames = [
#         [0, 0, 1, 1, 1, 0, 0, 0], [0, 0, 1, 0, 1, 0, 0, 0],  # block 1 fail → retry
#         [0, 1, 1, 1, 0, 0, 0, 0]  # block 2 ok
#     ]
#     physical_layer = DummyPhysicalLayer(expected_frames)
#     link = LinkLayer(physical_layer, parity_checksum, payload_size=4, seq_size=2, checksum_size=2, max_retries=2)
#     result = link.transmit(payload)
#     assert np.all(result == payload)
