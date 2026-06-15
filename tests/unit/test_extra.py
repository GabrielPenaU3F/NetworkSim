import numpy as np

from src.utils import int_to_bits, bits_to_int, pad_bits, unpad_bits


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
