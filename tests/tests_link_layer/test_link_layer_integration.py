import pytest
import numpy as np

def test_on_receive_unpads_correctly_on_several_frames(example_link_layer, tile_bits):
    bits = tile_bits(7)  # 14 bits
    frames = example_link_layer._build_frames(bits)

    result = None
    for f in frames:
        serialized = example_link_layer._serialize_frame(f)
        result = example_link_layer.on_receive(serialized)

    # In this architecture, the reception call of the last returns the complete message
    assert np.all(result == bits)

def test_total_serialized_length(example_link_layer, tile_bits):
    bits = tile_bits(7)  # 14 bits

    frames = example_link_layer._build_frames(bits)
    serialized_frames = [
        example_link_layer._serialize_frame(f)
        for f in frames
    ]

    full_stream = np.concatenate(serialized_frames)

    assert len(frames) == 2
    assert len(serialized_frames[0]) == 18
    assert len(serialized_frames[1]) == 18
    assert len(full_stream) == 36

def test_frame_roundtrip_with_real_config(example_link_layer, tile_bits):
    bits = tile_bits(7)
    frames = example_link_layer._build_frames(bits)

    for f in frames:
        serialized = example_link_layer._serialize_frame(f)
        deserialized = example_link_layer._deserialize_frame(serialized)
        assert deserialized.get_is_last() == f.get_is_last()

def test_rx_fails_with_fragmented_frames(example_link_layer, tile_bits):
    bits = tile_bits(7)  # 14 bits → 2 frames
    frames = example_link_layer._build_frames(bits)

    # Serialize
    serialized_frames = [example_link_layer._serialize_frame(f) for f in frames]
    full_stream = np.concatenate(serialized_frames)

    # Bits are fragmented into chunks
    chunk1 = full_stream[:10]
    chunk2 = full_stream[10:20]
    chunk3 = full_stream[20:]

    # First frame is not returned
    result = example_link_layer.on_receive(chunk1)
    assert result is None

    # Second frame is not returned
    result = example_link_layer.on_receive(chunk2)
    assert result is None

    # Last frame should be returned
    result = example_link_layer.on_receive(chunk3)
    assert result is not None
    assert np.all(result == bits)

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
