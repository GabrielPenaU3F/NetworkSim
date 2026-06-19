import numpy as np

from protocol_constants import ethernet
from utils import int_to_bits


class TestSerialization:

    def test_serialized_frame_has_correct_total_length(self, example_link_module, example_frame):
        serialized = example_link_module.serialize_frame(example_frame)
        expected_length = 48 + 48 + 16 + 8 + 8 + 1  # macs + ether_type + payload + checksum
        assert len(serialized) == expected_length

    def test_serialized_dst_mac_comes_first(self, example_link_module, example_frame):
        from src.utils import serialize_mac_address
        serialized = example_link_module.serialize_frame(example_frame)
        expected = serialize_mac_address('02:00:00:00:00:02', 48)
        assert np.all(serialized[:48] == expected)

    def test_serialized_src_mac_comes_second(self, example_link_module, example_frame):
        from src.utils import serialize_mac_address
        serialized = example_link_module.serialize_frame(example_frame)
        expected = serialize_mac_address('02:00:00:00:00:01', 48)
        assert np.all(serialized[48:96] == expected)

    def test_serialized_ether_type(self, example_link_module, example_frame):
        from src.utils import int_to_bits
        serialized = example_link_module.serialize_frame(example_frame)
        expected = int_to_bits(ethernet.IPV4, 16)
        assert np.all(serialized[96:112] == expected)

    def test_serialized_real_length(self, example_link_module, example_frame, tile_bits):
        serialized = example_link_module.serialize_frame(example_frame)
        expected_real_length = int_to_bits(8, 8)
        real_length = serialized[112:120]
        assert np.all(real_length == expected_real_length)

    def test_serialized_payload(self, example_link_module, example_frame, tile_bits):
        serialized = example_link_module.serialize_frame(example_frame)
        payload = serialized[120:128]
        assert np.all(payload == tile_bits(4))

    def test_serialized_checksum_is_one(self, example_link_module, example_frame):
        serialized = example_link_module.serialize_frame(example_frame)
        checksum = serialized[-1:]
        assert np.all(checksum == 1)


class TestDeserialization:

    def test_deserialize_recovers_dst_mac(self, example_link_module, frame_to_deserialize):
        deserialized = example_link_module.deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.dst_mac == '02:00:00:00:00:02'

    def test_deserialize_recovers_src_mac(self, example_link_module, frame_to_deserialize):
        deserialized = example_link_module.deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.src_mac == '02:00:00:00:00:01'

    def test_deserialize_recovers_ether_type(self, example_link_module, frame_to_deserialize):
        deserialized = example_link_module.deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.ether_type == ethernet.IPV4

    def test_deserialize_recovers_real_length(self, example_link_module, frame_to_deserialize, tile_bits):
        deserialized = example_link_module.deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.real_length == 8

    def test_deserialize_recovers_payload(self, example_link_module, frame_to_deserialize, tile_bits):
        deserialized = example_link_module.deserialize_frame(frame_to_deserialize, payload_size=8)
        assert np.all(deserialized.payload == tile_bits(4))

    def test_deserialize_recovers_checksum(self, example_link_module, frame_to_deserialize):
        deserialized = example_link_module.deserialize_frame(frame_to_deserialize, payload_size=8)
        assert deserialized.checksum == 1


class TestRoundtrip:

    def test_serialize_deserialize_roundtrip(self, example_link_module, example_frame):
        serialized = example_link_module.serialize_frame(example_frame)
        deserialized = example_link_module.deserialize_frame(serialized, payload_size=8)
        assert deserialized.dst_mac == example_frame.dst_mac
        assert deserialized.src_mac == example_frame.src_mac
        assert deserialized.ether_type == example_frame.ether_type
        assert deserialized.real_length == example_frame.real_length
        assert np.all(deserialized.payload == example_frame.payload)
        assert deserialized.checksum == example_frame.checksum
