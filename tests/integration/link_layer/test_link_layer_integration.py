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
        assert deserialized.is_last == f.is_last

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
