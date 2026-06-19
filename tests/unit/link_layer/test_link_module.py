import numpy as np
import pytest

from link_layer.link_module import LinkModule
from protocol_constants import ethernet
from tests.utilities.dummies import DummyChecksum
from utils import serialize_mac_address, int_to_bits


class TestBuildBody:

    def test_build_body_has_correct_total_length(self, example_link_module, tile_bits):
        payload = tile_bits(4)  # 8 bits
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        expected_length = example_link_module.header_size + len(payload)
        assert len(body) == expected_length

    def test_build_body_places_dst_mac_first(self, example_link_module, tile_bits):
        payload = tile_bits(4)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        mac_size = example_link_module.mac_size
        expected = serialize_mac_address('02:00:00:00:00:02', mac_size)
        assert np.all(body[:mac_size] == expected)

    def test_build_body_places_src_mac_second(self, example_link_module, tile_bits):
        payload = tile_bits(4)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', 0x0800, real_length=8, payload=payload
        )
        mac_size = example_link_module.mac_size
        expected = serialize_mac_address('02:00:00:00:00:01', mac_size)
        assert np.all(body[mac_size:mac_size * 2] == expected)

    def test_build_body_places_ether_type_after_macs(self, example_link_module, tile_bits):
        payload = tile_bits(4)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', ethernet.IPV4, real_length=8, payload=payload
        )
        start = example_link_module.mac_size * 2
        end = start + example_link_module.ether_type_size
        expected = int_to_bits(ethernet.IPV4, example_link_module.ether_type_size)
        assert np.all(body[start:end] == expected)

    def test_build_body_places_real_length_after_ether_type(self, example_link_module, tile_bits):
        payload = tile_bits(4)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', ethernet.IPV4, real_length=8, payload=payload
        )
        start = example_link_module.mac_size * 2 + example_link_module.ether_type_size
        end = start + example_link_module.real_length_size
        expected = int_to_bits(8, example_link_module.real_length_size)
        assert np.all(body[start:end] == expected)

    def test_build_body_places_payload_last(self, example_link_module, tile_bits):
        payload = tile_bits(4)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', ethernet.IPV4, real_length=8, payload=payload
        )
        assert np.all(body[example_link_module.header_size:] == payload)


class TestPeekRealLength:

    def test_peek_real_length_reads_correct_value(self, example_link_module, tile_bits):
        payload = tile_bits(4)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', ethernet.IPV4, real_length=8, payload=payload
        )
        header_bits = body[:example_link_module.header_size]
        assert example_link_module.peek_real_length(header_bits) == 8

    def test_peek_real_length_reads_zero(self, example_link_module, tile_bits):
        payload = np.zeros(example_link_module.min_payload_bits, dtype=np.uint8)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', ethernet.IPV4, real_length=0, payload=payload
        )
        header_bits = body[:example_link_module.header_size]
        assert example_link_module.peek_real_length(header_bits) == 0

    def test_peek_real_length_reads_maximum_payload_size(self, example_link_module, tile_bits):
        payload = np.zeros(example_link_module.max_payload_bits, dtype=np.uint8)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', ethernet.IPV4,
            real_length=example_link_module.max_payload_bits, payload=payload
        )
        header_bits = body[:example_link_module.header_size]
        assert example_link_module.peek_real_length(header_bits) == example_link_module.max_payload_bits

    def test_peek_real_length_only_reads_header_portion(self, example_link_module, tile_bits):
        # Even if extra bits (payload + checksum) are appended, peek should only look at the header
        payload = tile_bits(4)
        body = example_link_module._build_body(
            '02:00:00:00:00:01', '02:00:00:00:00:02', ethernet.IPV4, real_length=8, payload=payload
        )
        cs = example_link_module.compute_checksum(body)
        checksum_bits = int_to_bits(cs, example_link_module.checksum_size)
        full_frame = np.concatenate([body, checksum_bits])

        header_bits = full_frame[:example_link_module.header_size]
        assert example_link_module.peek_real_length(header_bits) == 8


class TestBuildFrame:

    def test_build_frame_header_fields(self, example_link_module, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        payload = tile_bits(8)  # 16 bits
        frame = example_link_module.build_frame(src_mac, dst_mac, ether_type, real_length=16, payload=payload)

        assert frame.src_mac == src_mac
        assert frame.dst_mac == dst_mac
        assert frame.ether_type == ether_type
        assert frame.real_length == 16

    def test_build_frame_checksum_is_computed_over_body(self, example_link_module, tile_bits, frame_header):
        src_mac, dst_mac, ether_type = frame_header
        payload = tile_bits(8)
        frame = example_link_module.build_frame(src_mac, dst_mac, ether_type, real_length=16, payload=payload)

        body_bits = example_link_module._build_body(src_mac, dst_mac, ether_type, 16, payload)
        assert frame.checksum == example_link_module.compute_checksum(body_bits)