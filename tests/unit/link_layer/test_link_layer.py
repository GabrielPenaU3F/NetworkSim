import numpy as np

from utils import int_to_bits, serialize_mac_address


class TestBuildBody:

    def test_build_body_has_correct_total_length(self, example_link_layer, tile_bits):
        payload = tile_bits(4)  # 8 bits
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        expected_length = example_link_layer.header_size + len(payload)
        assert len(body) == expected_length

    def test_build_body_places_dst_mac_first(self, example_link_layer, tile_bits):
        payload = tile_bits(4)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        mac_size = example_link_layer.mac_size
        expected = serialize_mac_address('02:00:00:00:00:02', mac_size)
        assert np.all(body[:mac_size] == expected)

    def test_build_body_places_src_mac_second(self, example_link_layer, tile_bits):
        payload = tile_bits(4)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        mac_size = example_link_layer.mac_size
        expected = serialize_mac_address('02:00:00:00:00:01', mac_size)
        assert np.all(body[mac_size:mac_size * 2] == expected)

    def test_build_body_places_ether_type_after_macs(self, example_link_layer, tile_bits):
        payload = tile_bits(4)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        start = example_link_layer.mac_size * 2
        end = start + example_link_layer.ether_type_size
        expected = int_to_bits(0x0800, example_link_layer.ether_type_size)
        assert np.all(body[start:end] == expected)

    def test_build_body_places_real_length_after_ether_type(self, example_link_layer, tile_bits):
        payload = tile_bits(4)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        start = example_link_layer.mac_size * 2 + example_link_layer.ether_type_size
        end = start + example_link_layer.real_length_size
        expected = int_to_bits(8, example_link_layer.real_length_size)
        assert np.all(body[start:end] == expected)

    def test_build_body_places_payload_last(self, example_link_layer, tile_bits):
        payload = tile_bits(4)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        assert np.all(body[example_link_layer.header_size:] == payload)


class TestPeekRealLength:

    def test_peek_real_length_reads_correct_value(self, example_link_layer, tile_bits):
        payload = tile_bits(4)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        header_bits = body[:example_link_layer.header_size]
        assert example_link_layer._peek_real_length(header_bits) == 8

    def test_peek_real_length_reads_zero(self, example_link_layer, tile_bits):
        payload = np.zeros(example_link_layer.min_payload_bits, dtype=np.uint8)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=0, payload=payload
        )
        header_bits = body[:example_link_layer.header_size]
        assert example_link_layer._peek_real_length(header_bits) == 0

    def test_peek_real_length_reads_maximum_payload_size(self, example_link_layer, tile_bits):
        payload = np.zeros(example_link_layer.max_payload_bits, dtype=np.uint8)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800,
            real_length=example_link_layer.max_payload_bits, payload=payload
        )
        header_bits = body[:example_link_layer.header_size]
        assert example_link_layer._peek_real_length(header_bits) == example_link_layer.max_payload_bits

    def test_peek_real_length_only_reads_header_portion(self, example_link_layer, tile_bits):
        # Even if extra bits (payload + checksum) are appended, peek should only look at the header
        payload = tile_bits(4)
        body = example_link_layer._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        cs = example_link_layer._compute_checksum(body)
        checksum_bits = int_to_bits(cs, example_link_layer.checksum_size)
        full_frame = np.concatenate([body, checksum_bits])

        header_bits = full_frame[:example_link_layer.header_size]
        assert example_link_layer._peek_real_length(header_bits) == 8


class TestBuildFrames:

    def test_build_a_single_frame_header(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        real_length = 16
        bits = tile_bits(8)
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        frame = eth_frames[0]

        assert frame.src_mac == src_mac
        assert frame.dst_mac == dst_mac
        assert frame.ether_type == ether_type
        assert frame.real_length == real_length

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

    def test_build_a_single_frame_checksum(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(8)
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        frame = eth_frames[0]
        body_bits = example_link_layer._build_body(src_mac, dst_mac, ether_type, 8, bits)
        assert frame.checksum == example_link_layer._compute_checksum(body_bits)

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

        for sent in physical.sent_bits:
            assert isinstance(sent, np.ndarray)


class TestLinkLayerRX:

    def test_single_frame_message_is_reconstructed(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(4)  # 8 bits, exact minimum
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized = example_link_layer._serialize_frame(frames[0])

        result = example_link_layer.on_receive(serialized)
        assert np.all(result == bits)

    def test_reception_removes_padding_on_short_message(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(2)  # 4 bits, below minimum, gets padded to 8
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized = example_link_layer._serialize_frame(frames[0])

        result = example_link_layer.on_receive(serialized)
        assert np.all(result == bits)
        assert len(result) == 4  # padding was stripped

    def test_multi_frame_message_is_reassembled_in_order(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(10)  # 20 bits -> 2 frames
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)

        result = None
        for frame in frames:
            serialized = example_link_layer._serialize_frame(frame)
            result = example_link_layer.on_receive(serialized)

        assert result is not None
        assert np.all(result == bits)

    def test_incomplete_stream_returns_none(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(10)  # 2 frames
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized_first = example_link_layer._serialize_frame(frames[0])

        result = example_link_layer.on_receive(serialized_first)
        assert result is None

    def test_fragmented_stream_arriving_in_chunks_is_reassembled(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(4)  # single frame, 8 bits + header + checksum
        frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        serialized = example_link_layer._serialize_frame(frames[0])

        midpoint = len(serialized) // 2
        first_chunk = serialized[:midpoint]
        second_chunk = serialized[midpoint:]

        result = example_link_layer.on_receive(first_chunk)
        assert result is None

        result = example_link_layer.on_receive(second_chunk)
        assert np.all(result == bits)