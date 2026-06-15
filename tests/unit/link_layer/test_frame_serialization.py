import numpy as np
import pytest

from link_layer.link_layer import LinkLayer
from src.link_layer.ether_frame import EthernetFrame


@pytest.fixture
def example_frame(tile_bits):
    return EthernetFrame(
        src_mac='02:00:00:00:00:01',
        dst_mac='02:00:00:00:00:02',
        ether_type=0x0800,
        payload=tile_bits(4),  # 8 bits
        checksum=0
    )

@pytest.fixture
def example_link_layer():
    return LinkLayer()

@pytest.fixture
def frame_to_deserialize(example_link_layer, example_frame):
    return example_link_layer._serialize_frame(example_frame)


class TestSerialization:

    def test_serialized_frame_has_correct_total_length(self, example_link_layer, example_frame):
        serialized = example_link_layer._serialize_frame(example_frame)
        expected_length = 48 + 48 + 16 + 8 + 32  # macs + ether_type + payload + checksum
        assert len(serialized) == expected_length

    def test_serialized_dst_mac_comes_first(self, example_link_layer, example_frame):
        from src.utils import serialize_mac_address
        serialized = example_link_layer._serialize_frame(example_frame)
        expected = serialize_mac_address('02:00:00:00:00:02', 48)
        assert np.all(serialized[:48] == expected)

    def test_serialized_src_mac_comes_second(self, example_link_layer, example_frame):
        from src.utils import serialize_mac_address
        serialized = example_link_layer._serialize_frame(example_frame)
        expected = serialize_mac_address('02:00:00:00:00:01', 48)
        assert np.all(serialized[48:96] == expected)

    def test_serialized_ether_type(self, example_link_layer, example_frame):
        from src.utils import int_to_bits
        serialized = example_link_layer._serialize_frame(example_frame)
        expected = int_to_bits(0x0800, 16)
        assert np.all(serialized[96:112] == expected)

    def test_serialized_payload(self, example_link_layer, example_frame, tile_bits):
        serialized = example_link_layer._serialize_frame(example_frame)
        payload = serialized[112:120]
        assert np.all(payload == tile_bits(4))

    def test_serialized_checksum_is_zero_by_default(self, example_link_layer, example_frame):
        serialized = example_link_layer._serialize_frame(example_frame)
        checksum = serialized[-32:]
        assert np.all(checksum == 0)


class TestDeserialization:

    def test_deserialize_recovers_dst_mac(self, example_link_layer, frame_to_deserialize):
        deserialized = example_link_layer._deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.dst_mac == '02:00:00:00:00:02'

    def test_deserialize_recovers_src_mac(self, example_link_layer, frame_to_deserialize):
        deserialized = example_link_layer._deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.src_mac == '02:00:00:00:00:01'

    def test_deserialize_recovers_ether_type(self, example_link_layer, frame_to_deserialize):
        deserialized = example_link_layer._deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.ether_type == 0x0800

    def test_deserialize_recovers_payload(self, example_link_layer, frame_to_deserialize, tile_bits):
        deserialized = example_link_layer._deserialize_frame(frame_to_deserialize, payload_size=8)
        assert np.all(deserialized.payload == tile_bits(4))

    def test_deserialize_recovers_checksum(self, example_link_layer, frame_to_deserialize):
        deserialized = example_link_layer._deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.checksum == 0


class TestRoundtrip:

    def test_serialize_deserialize_roundtrip(self, example_link_layer, example_frame):
        serialized = example_link_layer._serialize_frame(example_frame)
        deserialized = example_link_layer._deserialize_frame(serialized, payload_size=8)
        assert deserialized.dst_mac == example_frame.dst_mac
        assert deserialized.src_mac == example_frame.src_mac
        assert deserialized.ether_type == example_frame.ether_type
        assert np.all(deserialized.payload == example_frame.payload)
        assert deserialized.checksum == example_frame.checksum

    def test_roundtrip_with_nonzero_checksum(self, example_link_layer, tile_bits):
        frame = EthernetFrame(
            src_mac='02:00:00:00:00:01',
            dst_mac='ff:ff:ff:ff:ff:ff',
            ether_type=0x0806,
            payload=tile_bits(4),
            checksum=123456
        )
        serialized = example_link_layer._serialize_frame(frame)
        deserialized = example_link_layer._deserialize_frame(serialized, payload_size=8)
        assert deserialized.checksum == 123456