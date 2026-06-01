import numpy as np
import pytest

from src.utils import int_to_bits, bits_to_int, pad_bits, unpad_bits, serialize_ip_address, deserialize_ip_address


def test_4_in_4_bits_int2bit():
    bits = int_to_bits(4, 4)
    assert np.all(bits == [0, 1, 0, 0])

def test_3_in_8_bits_int2bit():
    bits = int_to_bits(3, 8)
    assert np.all(bits == [0, 0, 0, 0, 0, 0, 1, 1])

def test_4_in_4_bits_bit2int():
    four = bits_to_int([0, 1, 0, 0])
    assert four == 4

def test_3_in_8_bits_bit2int():
    three = bits_to_int([0, 0, 0, 0, 0, 0, 1, 1])
    assert three == 3

def test_padding():
    padded, padding = pad_bits([1, 0, 1, 0, 1], 4)
    assert np.all(padded == [1, 0, 1, 0, 1, 0, 0, 0])
    assert padding == 3

def test_unpadding():
    result = unpad_bits([1, 0, 1, 0, 1, 0, 0, 0], 3)
    assert np.all(result == [1, 0, 1, 0, 1])

def test_serialized_ips_use_the_correct_field_size():
    address_1 = '0.0.0'
    address_2 = '0.0'
    serialized_1 = serialize_ip_address(address_1, 24)
    serialized_2 = serialize_ip_address(address_2, 16)
    assert len(serialized_1) == 24
    assert len(serialized_2) == 16

def test_serialize_zero_ip():
    address = '0.0.0.0'
    serialized = serialize_ip_address(address, 32)
    assert np.all(serialized == np.zeros(32))

def test_serialize_maximum_ip():
    address = '255.255.255.255'
    serialized = serialize_ip_address(address, 32)
    assert np.all(serialized == np.ones(32))

def test_serialize_ip_with_insufficient_bits_raises_error():
    with pytest.raises(ValueError, match='16 bits are not enough to represent 4 parts of 8 bits each'):
        serialize_ip_address('0.0.0.0', 16)

def test_serialize_ip_with_invalid_part_raises_error():
    with pytest.raises(ValueError, match='Each part must be between 0 and 255'):
        serialize_ip_address('256.0.0.0', 32)

def test_serialize_ip_with_negative_part_raises_error():
    with pytest.raises(ValueError, match='Each part must be between 0 and 255'):
        serialize_ip_address('-1.0.0.0', 32)

def test_deserialize_zero_ip():
    bits = np.zeros(32, dtype=np.uint8)
    assert deserialize_ip_address(bits) == '0.0.0.0'

def test_deserialize_maximum_ip():
    bits = np.ones(32, dtype=np.uint8)
    assert deserialize_ip_address(bits) == '255.255.255.255'

def test_serialize_deserialize_roundtrip():
    address = '192.168.0.1'
    bits = serialize_ip_address(address, 32)
    recovered = deserialize_ip_address(bits)
    assert recovered == address

def test_serialize_deserialize_roundtrip_two_parts():
    address = '192.168'
    bits = serialize_ip_address(address, 16)
    recovered = deserialize_ip_address(bits, num_parts=2)
    assert recovered == address

def test_deserialize_with_insufficient_bits_raises_error():
    bits = np.zeros(16, dtype=np.uint8)
    with pytest.raises(ValueError, match='16 bits are not enough to deserialize 4 parts of 8 bits each'):
        deserialize_ip_address(bits, num_parts=4)
