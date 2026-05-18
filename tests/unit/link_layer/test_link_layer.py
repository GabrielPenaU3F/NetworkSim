import numpy as np
import pytest

from src.errors import LinkError
from tests.unit.link_layer.conftest import frame_to_serialize


class TestSerialization:

    def test_serialize_frame_seq(self, example_link_layer, frame_to_serialize):
        expected_seq = np.array([0, 0], dtype=np.uint8)
        serialized = example_link_layer._serialize_frame(frame_to_serialize(is_last=1))
        seq_end = example_link_layer.seq_size
        actual_seq = serialized[:seq_end]
        assert np.all(actual_seq == expected_seq)

    def test_serialize_frame_is_last(self, example_link_layer, frame_to_serialize):
        serialized = example_link_layer._serialize_frame(frame_to_serialize(is_last=1))
        seq_end = example_link_layer.seq_size
        actual_is_last = serialized[seq_end]
        assert actual_is_last == 1

    def test_serialize_frame_is_not_last(self, example_link_layer, frame_to_serialize):
        serialized = example_link_layer._serialize_frame(frame_to_serialize(is_last=0))
        seq_end = example_link_layer.seq_size
        actual_is_last = serialized[seq_end]
        assert actual_is_last == 0

    def test_serialize_frame_is_ack(self, example_link_layer, frame_to_serialize):
        serialized = example_link_layer._serialize_frame(frame_to_serialize(is_ack=1))
        seq_end = example_link_layer.seq_size
        actual_is_ack = serialized[1 + seq_end]
        assert actual_is_ack == 1

    def test_serialize_frame_is_not_ack(self, example_link_layer, frame_to_serialize):
        serialized = example_link_layer._serialize_frame(frame_to_serialize(is_ack=0))
        seq_end = example_link_layer.seq_size
        actual_is_ack = serialized[1 + seq_end]
        assert actual_is_ack == 0

    def test_serialize_frame_real_length(self, example_link_layer, frame_to_serialize):
        # Size is ceil(log2(1 + payload_size)), thus, 4 binary digits. So 4 in binary (with four digits) is 0100
        expected_real_length = np.array([0, 1, 0, 0], dtype=np.uint8)
        serialized = example_link_layer._serialize_frame(frame_to_serialize(is_last=1))

        real_length_size = example_link_layer.payload_length_field_size
        real_length_end = example_link_layer._get_header_size()
        real_length_start = example_link_layer._get_header_size() - real_length_size

        actual_real_length = serialized[real_length_start: real_length_end]
        assert np.all(actual_real_length == expected_real_length)

    def test_serialize_frame_payload(self, example_link_layer, frame_to_serialize):
        frame = frame_to_serialize(is_last=1)
        expected_payload = frame.get_payload()
        serialized = example_link_layer._serialize_frame(frame)

        payload_end = example_link_layer._get_body_size()
        payload_start = payload_end - example_link_layer.payload_size

        actual_payload = serialized[payload_start: payload_end]
        assert np.all(actual_payload == expected_payload)

    def test_serialize_frame_checksum(self, example_link_layer, frame_to_serialize):
        expected_checksum = np.array([0, 0], dtype=np.uint8)
        serialized = example_link_layer._serialize_frame(frame_to_serialize(is_last=1))
        payload_end = example_link_layer._get_body_size()

        actual_checksum = serialized[payload_end:]
        assert np.all(actual_checksum == expected_checksum)


class TestDeserialization:

    def test_deserialize_frame_seq(self, example_link_layer, serialized_bits):
        deserialized = example_link_layer._deserialize_frame(serialized_bits())
        assert deserialized.get_seq() == 0

    def test_deserialize_frame_is_last(self, example_link_layer, serialized_bits):
        deserialized = example_link_layer._deserialize_frame(serialized_bits(is_last=1))
        assert deserialized.get_is_last() == 1

    def test_deserialize_frame_is_not_last(self, example_link_layer, serialized_bits):
        deserialized = example_link_layer._deserialize_frame(serialized_bits(is_last=0))
        assert deserialized.get_is_last() == 0

    def test_deserialize_frame_is_ack(self, example_link_layer, serialized_bits):
        deserialized = example_link_layer._deserialize_frame(serialized_bits(is_ack=1))
        assert deserialized.get_is_ack() == 1

    def test_deserialize_frame_is_not_ack(self, example_link_layer, serialized_bits):
        deserialized = example_link_layer._deserialize_frame(serialized_bits(is_ack=0))
        assert deserialized.get_is_ack() == 0

    def test_deserialize_frame_real_length(self, example_link_layer, serialized_bits):
        deserialized = example_link_layer._deserialize_frame(serialized_bits())
        assert deserialized.get_real_length() == 4

    def test_deserialize_frame_payload(self, example_link_layer, serialized_bits):
        deserialized = example_link_layer._deserialize_frame(serialized_bits())
        expected_payload = np.array([0, 1, 0, 1], dtype=np.uint8)
        assert np.all(deserialized.get_payload() == expected_payload)


class TestChecksumCalculation:

    def test_build_body_structure(self, example_link_layer):
        seq = 0
        is_last = 1
        is_ack = 0
        real_length = 4
        payload = np.array([0, 1, 0, 1, 0, 0, 0, 0], dtype=np.uint8)

        body = example_link_layer._build_body(seq, is_last, is_ack, real_length, payload)

        expected = np.array([
            0, 0,  # seq (2 bits)
            1,  # is_last
            0, # is_ack
            0, 1, 0, 0,  # real_length = 4
            0, 1, 0, 1, 0, 0, 0, 0  # payload
        ], dtype=np.uint8)

        assert np.all(body == expected)

    def test_checksum_changes_with_seq(self, example_link_layer, base_body):
        body_with_different_seq = base_body.copy()
        body_with_different_seq[0] ^= 1  # flip a bit from seq
        cs1 = example_link_layer._compute_checksum(base_body)
        cs2 = example_link_layer._compute_checksum(body_with_different_seq)

        assert not np.all(cs1 == cs2)

    def test_checksum_changes_with_is_last(self, example_link_layer, base_body):
        body_with_islast_0 = base_body.copy()
        is_last_idx = example_link_layer.seq_size
        body_with_islast_0[is_last_idx] ^= 1  # flip is_last
        cs1 = example_link_layer._compute_checksum(base_body)
        cs2 = example_link_layer._compute_checksum(body_with_islast_0)

        assert not np.all(cs1 == cs2)

    def test_checksum_changes_with_is_ack(self, example_link_layer, base_body):
        body_with_isack_1 = base_body.copy()
        is_ack_idx = example_link_layer.seq_size + 1
        body_with_isack_1[is_ack_idx] ^= 1  # flip is_ack
        cs1 = example_link_layer._compute_checksum(base_body)
        cs2 = example_link_layer._compute_checksum(body_with_isack_1)

        assert not np.all(cs1 == cs2)

    def test_checksum_changes_with_real_length(self, example_link_layer, base_body):
        body_with_different_real_length = base_body.copy()
        real_length_idx = example_link_layer._get_header_size() - 1
        body_with_different_real_length[real_length_idx] ^= 1  # flip a bit from real_length
        cs1 = example_link_layer._compute_checksum(base_body)
        cs2 = example_link_layer._compute_checksum(body_with_different_real_length)

        assert not np.all(cs1 == cs2)

    def test_checksum_changes_with_payload(self, example_link_layer, base_body):
        body_with_different_payload = base_body.copy()
        body_with_different_payload[-1] ^= 1  # flip last payload bit
        cs1 = example_link_layer._compute_checksum(base_body)
        cs2 = example_link_layer._compute_checksum(body_with_different_payload)

        assert not np.all(cs1 == cs2)


class TestLinkLayer:

    def test_build_a_single_frame_header(self, example_link_layer, tile_bits):
        bits = tile_bits(2)
        frames = example_link_layer._build_frames(bits)
        frame = frames[0]

        assert frame.get_seq() == 0
        assert frame.get_is_last() == 1
        assert frame.get_real_length() == 4

    def test_build_a_single_frame_payload_without_padding(self, example_link_layer, tile_bits):
        bits = tile_bits(4) # Exactly 8 bits on a link layer with payload_size=8
        frames = example_link_layer._build_frames(bits)
        frame = frames[0]
        assert np.all(frame.get_payload() == bits)

    def test_build_a_single_frame_payload_with_padding(self, example_link_layer, tile_bits):
        bits = tile_bits(2) # 4 bits on a link layer with payload_size=8, needs padding
        frames = example_link_layer._build_frames(bits)
        frame = frames[0]
        expected_payload = np.concatenate(([0, 1, 0, 1], [0, 0, 0, 0]))
        assert np.all(frame.get_payload() == expected_payload)

    def test_build_frames(self, example_link_layer, tile_bits):
        bits = tile_bits(7)
        frames = example_link_layer._build_frames(bits)
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

    def test_link_tx_serializes_and_sends_downwards(self, example_link_layer):
        bits = np.array(np.zeros(16), dtype=np.uint8)

        # Monkeypatch ack reception
        acked = set()
        def fake_ack(frame):
            seq = frame.get_seq()
            if seq in acked:
                return True

            acked.add(seq)
            return False

        example_link_layer._ack_received = fake_ack

        example_link_layer.transmit(bits)
        physical = example_link_layer.lower_layer
        assert len(physical.sent_bits) > 0 # something was sent

        for sent in physical.sent_bits:
            assert isinstance(sent, np.ndarray) # sent stuff are bit arrays

        assert physical.calls >= 2 # at least 2 calls

    def test_reception_removes_padding_single_frame(self, example_link_layer, serialized_bits):
        # payload_size = 8, only 4 real bits
        message = example_link_layer.on_receive(serialized_bits(1))
        expected = np.array([0, 1, 0, 1], dtype=np.uint8)

        assert np.all(message == expected)

    def test_parity_checksum_detects_error(self, example_link_layer, serialized_bits):
        corrupted = serialized_bits(0).copy()
        corrupted[5] ^= 1

        result = example_link_layer.on_receive(corrupted)
        assert result is None

    def test_parity_checksum_does_not_detect_error_when_two_bits_flip(self, example_link_layer, serialized_bits):
        corrupted = serialized_bits(0).copy()
        corrupted[5] ^= 1
        corrupted[2] ^= 1

        result = example_link_layer.on_receive(corrupted)
        assert result is not None

    def test_no_retry_when_ack_received(self, example_link_layer, tile_bits):
        bits = tile_bits(2)  # 1 frame
        physical = example_link_layer.lower_layer

        # We monkeypatch the transmission method of the physical layer
        # It sends an immediate ack. Then the link layer should stop transmitting.
        def transmit_with_ack(bits_sent, interface=None):
            physical.sent_bits.append(bits_sent)
            physical.calls += 1

            # immediate ACK
            frame = example_link_layer._deserialize_frame(bits_sent)
            ack = example_link_layer._build_ack(frame.get_seq())
            ack_bits = example_link_layer._serialize_frame(ack)

            example_link_layer.on_receive(ack_bits)

        # monkeypatch
        physical.transmit = transmit_with_ack
        example_link_layer._validate_checksum = lambda x: True  # Do not check anything
        example_link_layer.transmit(bits)

        # A single call
        assert physical.calls == 1

    def test_no_duplicate_payload_on_retry(self, example_link_layer, frame_to_serialize):
        frame = frame_to_serialize(is_last=0)
        serialized = example_link_layer._serialize_frame(frame)

        # do not check anything
        example_link_layer._validate_checksum = lambda x: True

        # RX receives a duplicate frame
        example_link_layer.on_receive(serialized)
        example_link_layer.on_receive(serialized)

        # Manually rebuild
        result = example_link_layer._rebuild_message()

        expected_payload = np.tile([0, 1], 2)
        assert np.all(result == expected_payload)

    def test_rx_sends_an_ack(self, example_link_layer, frame_to_serialize):
        frame = frame_to_serialize()
        serialized = example_link_layer._serialize_frame(frame)

        physical = example_link_layer.lower_layer

        # do not check anything
        example_link_layer._validate_checksum = lambda x: True
        example_link_layer.on_receive(serialized)

        # RX should have transmitted exactly one ACK
        assert physical.calls == 1

    def test_rx_sends_correct_ack(self, example_link_layer, frame_to_serialize):
        frame = frame_to_serialize(seq=3, is_last=0)
        serialized = example_link_layer._serialize_frame(frame)

        physical = example_link_layer.lower_layer

        # do not check anything
        example_link_layer._validate_checksum = lambda x: True
        example_link_layer.on_receive(serialized)

        ack_bits = physical.sent_bits[0]
        ack_frame = example_link_layer._deserialize_frame(ack_bits)

        assert ack_frame.get_is_ack() == 1
        assert ack_frame.get_seq() == 3

    def test_rx_reacknowledges_duplicate_frames(self, example_link_layer, frame_to_serialize):
        frame = frame_to_serialize(seq=3, is_last=0)
        serialized = example_link_layer._serialize_frame(frame)

        physical = example_link_layer.lower_layer

        # do not check anything
        example_link_layer._validate_checksum = lambda x: True

        # receive twice the same frame
        example_link_layer.on_receive(serialized)
        example_link_layer.on_receive(serialized)

        # ack should be sent twice (despite being the same frame)
        assert physical.calls == 2

    def test_tx_raises_after_max_retries(self, example_link_layer, tile_bits):
        bits = tile_bits(2)  # 1 frame
        physical = example_link_layer.lower_layer

        # ack not received
        example_link_layer._ack_received = lambda frame: False

        with pytest.raises(LinkError):
            example_link_layer.transmit(bits)

        # exactly max_retries transmissions
        assert physical.calls == example_link_layer.max_retries

    def test_build_ack_generates_valid_checksum(self, example_link_layer):
        ack = example_link_layer._build_ack(seq=3)
        serialized = example_link_layer._serialize_frame(ack)
        assert example_link_layer._validate_checksum(serialized)

    def test_build_ack_sets_correct_fields(self, example_link_layer):
        ack = example_link_layer._build_ack(seq=5)

        assert ack.get_seq() == 5
        assert ack.get_is_ack() == 1
        assert ack.get_is_last() == 0
        assert ack.get_real_length() == 0

    def test_build_ack_uses_empty_payload(self, example_link_layer):
        ack = example_link_layer._build_ack(seq=1)
        expected = np.zeros(example_link_layer.payload_size, dtype=np.uint8)

        assert np.all(ack.get_payload() == expected)
