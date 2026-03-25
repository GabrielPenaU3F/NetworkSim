import numpy as np
import pytest

from src.physical_layer.codes.channel_codes import (
    NoChannelCode,
    RepetitionChannelCode, HammingChannelCode
)


@pytest.fixture
def bits():
    return [0, 1, 0, 1, 1, 0, 1]

@pytest.fixture
def no_code():
    return NoChannelCode()


@pytest.fixture
def repetition_code():
    return RepetitionChannelCode(r=3)

@pytest.fixture
def hamming_code():
    return HammingChannelCode()


class TestNoChannelCode:

    def test_encode_identity(self, no_code, bits):
        assert no_code.encode_bits(bits) == bits

    def test_decode_identity(self, no_code, bits):
        assert no_code.decode_bits(bits) == bits

    def test_encode_decode_pipeline(self, no_code, bits):
        encoded = no_code.encode_bits(bits)
        decoded = no_code.decode_bits(encoded)
        assert decoded == bits


class TestRepetitionChannelCode:

    def test_encoding_length(self, repetition_code, bits):
        encoded = repetition_code.encode_bits(bits)
        assert len(encoded) == len(bits) * repetition_code.r


    def test_encoding_structure(self, repetition_code):
        bits = [0, 1]
        encoded = repetition_code.encode_bits(bits)
        # "0" -> "000", "1" -> "111"
        assert np.all(encoded == [0, 0, 0, 1, 1, 1])

    def test_decode_no_noise(self, repetition_code, bits):
        encoded = repetition_code.encode_bits(bits)
        decoded = repetition_code.decode_bits(encoded)
        assert np.all(decoded == bits)

    def test_decode_majority_vote(self, repetition_code):
        noisy = [1, 0, 1]
        decoded = repetition_code.decode_bits(noisy) # Vote decoding should decide on 1
        assert decoded == [1]

    def test_repetition_r_is_odd(self):
        code = RepetitionChannelCode(r=3)
        assert code.r % 2 == 1

    def test_repetition_r_is_not_odd(self):
        with pytest.raises(ValueError):
            RepetitionChannelCode(r=4)


class TestHammingChannelCode:

    def test_hamming_no_error(self, hamming_code):
        bits = [1, 0, 1, 1, 0, 0, 1, 1]
        decoded = hamming_code.decode_bits(hamming_code.encode_bits(bits))
        assert np.all(decoded[:len(bits)] == bits)

    def test_hamming_corrects_single_error(self, hamming_code):
        bits = [1, 0, 1, 1]
        encoded = hamming_code.encode_bits(bits)
        encoded[2] = encoded[2] ^ 1 # 1 bit error
        decoded = hamming_code.decode_bits(encoded)
        assert np.all(decoded[:len(bits)] == bits)

    def test_hamming_fails_double_error(self, hamming_code):
        bits = [1, 0, 1, 1]
        encoded = hamming_code.encode_bits(bits)
        encoded[1] = encoded[1] ^ 1 # 2 bit errors
        encoded[2] = encoded[2] ^ 1 # 2 bit errors
        decoded = hamming_code.decode_bits(encoded)
        assert np.any(decoded[:len(bits)] == bits)
