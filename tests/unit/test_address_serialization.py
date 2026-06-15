import re

import pytest

import numpy as np

from src.utils import serialize_ip_address, deserialize_ip_address
from src.utils import serialize_mac_address, deserialize_mac_address


class TestMACSerialization:

    def test_serialize_zero_mac(self):
        mac = '00:00:00:00:00:00'
        serialized = serialize_mac_address(mac)
        assert np.all(serialized == np.zeros(48))

    def test_serialize_maximum_mac(self):
        mac = 'ff:ff:ff:ff:ff:ff'
        serialized = serialize_mac_address(mac)
        assert np.all(serialized == np.ones(48))

    def test_serialized_mac_has_correct_length(self):
        mac = '02:00:00:00:00:01'
        serialized = serialize_mac_address(mac)
        assert len(serialized) == 48

    def test_serialize_mac_with_insufficient_bits_raises_error(self):
        with pytest.raises(ValueError, match='32 bits are not enough to represent 6 parts of 8 bits each'):
            serialize_mac_address('02:00:00:00:00:01', 32)

    def test_serialize_mac_with_invalid_part_raises_error(self):
        with pytest.raises(ValueError, match=re.escape("invalid literal for int() with base 16: 'gg'")):
            serialize_mac_address('gg:00:00:00:00:01')

    def test_deserialize_zero_mac(self):
        bits = np.zeros(48, dtype=np.uint8)
        assert deserialize_mac_address(bits) == '00:00:00:00:00:00'

    def test_deserialize_maximum_mac(self):
        bits = np.ones(48, dtype=np.uint8)
        assert deserialize_mac_address(bits) == 'ff:ff:ff:ff:ff:ff'

    def test_serialize_deserialize_mac_roundtrip(self):
        mac = '02:00:00:0a:1b:2c'
        bits = serialize_mac_address(mac)
        recovered = deserialize_mac_address(bits)
        assert recovered == mac

    def test_deserialize_mac_with_insufficient_bits_raises_error(self):
        bits = np.zeros(32, dtype=np.uint8)
        with pytest.raises(ValueError, match='32 bits are not enough to deserialize 6 parts of 8 bits each'):
            deserialize_mac_address(bits, num_parts=6)


class TestIPSerialization:

    def test_serialized_ips_use_the_correct_field_size(self):
        address_1 = '0.0.0'
        address_2 = '0.0'
        serialized_1 = serialize_ip_address(address_1, 24)
        serialized_2 = serialize_ip_address(address_2, 16)
        assert len(serialized_1) == 24
        assert len(serialized_2) == 16

    def test_serialize_zero_ip(self):
        address = '0.0.0.0'
        serialized = serialize_ip_address(address, 32)
        assert np.all(serialized == np.zeros(32))

    def test_serialize_maximum_ip(self):
        address = '255.255.255.255'
        serialized = serialize_ip_address(address, 32)
        assert np.all(serialized == np.ones(32))

    def test_serialize_ip_with_insufficient_bits_raises_error(self):
        with pytest.raises(ValueError, match='16 bits are not enough to represent 4 parts of 8 bits each'):
            serialize_ip_address('0.0.0.0', 16)

    def test_serialize_ip_with_invalid_part_raises_error(self):
        with pytest.raises(ValueError, match='Each part must be between 0 and 255'):
            serialize_ip_address('256.0.0.0', 32)

    def test_serialize_ip_with_negative_part_raises_error(self):
        with pytest.raises(ValueError, match='Each part must be between 0 and 255'):
            serialize_ip_address('-1.0.0.0', 32)

    def test_deserialize_zero_ip(self):
        bits = np.zeros(32, dtype=np.uint8)
        assert deserialize_ip_address(bits) == '0.0.0.0'

    def test_deserialize_maximum_ip(self):
        bits = np.ones(32, dtype=np.uint8)
        assert deserialize_ip_address(bits) == '255.255.255.255'

    def test_serialize_deserialize_roundtrip(self):
        address = '192.168.0.1'
        bits = serialize_ip_address(address, 32)
        recovered = deserialize_ip_address(bits)
        assert recovered == address

    def test_serialize_deserialize_roundtrip_two_parts(self):
        address = '192.168'
        bits = serialize_ip_address(address, 16)
        recovered = deserialize_ip_address(bits, num_parts=2)
        assert recovered == address

    def test_deserialize_with_insufficient_bits_raises_error(self):
        bits = np.zeros(16, dtype=np.uint8)
        with pytest.raises(ValueError, match='16 bits are not enough to deserialize 4 parts of 8 bits each'):
            deserialize_ip_address(bits, num_parts=4)
