import numpy as np
import pytest

from protocol_constants import ethernet


@pytest.fixture
def frame_header():
    src_mac = '02:00:00:00:00:01'
    dst_mac = '02:00:00:00:00:02'
    ether_type = 0x0800
    return (
        src_mac,
        dst_mac,
        ether_type,
    )

class TestLinkLayer:

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
        # assert frame.checksum == frame._compute_checksum(frame.serialize_body())

    def test_build_a_single_frame_payload_is_padded_to_minimum(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = tile_bits(8)  # 16 bits < MIN_PAYLOAD_BITS
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        frame = eth_frames[0]

        assert len(frame.payload) == ethernet.MIN_PAYLOAD_BITS
        assert np.all(frame.payload[:16] == bits)
        assert np.all(frame.payload[16:] == 0)

    def test_build_a_single_frame_without_padding(self, example_link_layer, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = np.zeros(ethernet.MIN_PAYLOAD_BITS, dtype=np.uint8)
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        frame = eth_frames[0]

        assert len(frame.payload) == ethernet.MIN_PAYLOAD_BITS
        assert frame.real_length == ethernet.MIN_PAYLOAD_BITS

    def test_build_a_single_frame_checksum(self, example_link_layer, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        real_length = 16
        bits = tile_bits(8)
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        frame = eth_frames[0]

        assert frame.checksum == frame._compute_checksum()

    def test_build_two_frames(self, example_link_layer, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        bits = np.ones(1500 * 8 + 600).astype(np.uint8)
        eth_frames = example_link_layer._build_frames(bits, src_mac, dst_mac, ether_type)
        f0, f1 = eth_frames

        # ------------------
        # Frame 0 (payload field is full)
        # ------------------
        expected_payload_0 = bits[:1500 * 8]

        assert np.all(f0.payload == expected_payload_0)

        # ------------------
        # Frame 1 (with no padding)
        # ------------------
        expected_payload_1 = bits[-600:]

        assert f1.real_length == 600
        assert np.all(f1.payload == expected_payload_1)