import numpy as np


def test_build_frames_delegates_consistently_with_link_module(example_link_layer, tile_bits, frame_header):
    src_mac, dst_mac, ether_type = frame_header
    bits = tile_bits(4)  # 8 bits, single frame, no padding needed
    frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)

    direct_frame = example_link_layer._link_module.build_frame(src_mac, dst_mac, ether_type, 8, bits)

    assert frames[0].real_length == direct_frame.real_length
    assert np.all(frames[0].payload == direct_frame.payload)
    assert frames[0].checksum == direct_frame.checksum


class TestBuildFrames:


    def test_build_a_single_frame_payload_is_padded_to_minimum(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(2)  # 4 bits < MIN_PAYLOAD_BITS
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        frame = eth_frames[0]

        assert len(frame.payload) == 8
        assert np.all(frame.payload[:4] == bits)
        assert np.all(frame.payload[4:] == 0)

    def test_build_a_single_frame_without_padding(self, example_link_layer, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = np.zeros(8, dtype=np.uint8)
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        frame = eth_frames[0]

        assert len(frame.payload) == 8
        assert frame.real_length == 8

    def test_message_larger_than_max_is_split_into_multiple_frames(self, example_link_layer, frame_header, tile_bits):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(10)  # 20 bits > max_payload_bits (16)
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)

        assert len(frames) == 2
        assert frames[0].real_length == 16
        assert len(frames[0].payload) == 16
        assert frames[1].real_length == 4
        assert len(frames[1].payload) == 8  # padded up to min_payload_bits

    def test_last_frame_with_intermediate_size_is_not_padded(self, example_link_layer, frame_header, tile_bits):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(14)  # 28 bits: first frame 16, second frame 12 (between min=8 and max=16)
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)

        assert len(frames) == 2
        assert frames[0].real_length == 16
        assert frames[1].real_length == 12
        assert len(frames[1].payload) == 12  # no padding needed, already above minimum


class TestLinkLayerTX:

    def test_transmit_sends_one_call_per_frame(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(10)  # 2 frames expected
        physical = example_link_layer.lower_layer
        example_link_layer.transmit(bits, interface=None, src_mac=src_mac, dst_mac=dst_mac, ether_type=ether_type)

        assert physical.calls == 2

    def test_transmit_sends_bit_arrays(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(4)
        physical = example_link_layer.lower_layer

        example_link_layer.transmit(bits, interface=None, src_mac=src_mac, dst_mac=dst_mac, ether_type=ether_type)

        for sent in physical.last_sent_bits:
            assert isinstance(sent, np.ndarray)


class TestLinkLayerRX:

    def test_single_frame_message_is_reconstructed(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(4)  # 8 bits, exact minimum
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized = example_link_layer._link_module.serialize_frame(frames[0])

        result = example_link_layer.on_receive(serialized)
        assert np.all(result == bits)

    def test_reception_removes_padding_on_short_message(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(2)  # 4 bits, below minimum, gets padded to 8
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized = example_link_layer._link_module.serialize_frame(frames[0])

        result = example_link_layer.on_receive(serialized)
        assert np.all(result == bits)
        assert len(result) == 4  # padding was stripped

    def test_multi_frame_message_is_reassembled_in_order(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(10)  # 20 bits -> 2 frames
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)

        result = None
        for frame in frames:
            serialized = example_link_layer._link_module.serialize_frame(frame)
            result = example_link_layer.on_receive(serialized)

        assert result is not None
        assert np.all(result == bits)

    def test_incomplete_stream_returns_none(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(10)  # 2 frames
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized_first = example_link_layer._link_module.serialize_frame(frames[0])

        result = example_link_layer.on_receive(serialized_first)
        assert result is None

    def test_fragmented_stream_arriving_in_chunks_is_reassembled(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(4)  # single frame, 8 bits + header + checksum
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized = example_link_layer._link_module.serialize_frame(frames[0])

        midpoint = len(serialized) // 2
        first_chunk = serialized[:midpoint]
        second_chunk = serialized[midpoint:]

        result = example_link_layer.on_receive(first_chunk)
        assert result is None

        result = example_link_layer.on_receive(second_chunk)
        assert np.all(result == bits)