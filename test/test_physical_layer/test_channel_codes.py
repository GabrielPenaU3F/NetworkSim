import pytest

from src.physical_layer.codes.channel_codes import (
    NoChannelCode,
    RepetitionChannelCode
)


@pytest.fixture
def bits():
    return "0101101"


@pytest.fixture
def no_code():
    return NoChannelCode()


@pytest.fixture
def repetition_code():
    return RepetitionChannelCode(r=3)


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
        bits = "01"
        encoded = repetition_code.encode_bits(bits)
        # "0" -> "000", "1" -> "111"
        assert encoded == "000111"

    def test_decode_no_noise(self, repetition_code, bits):
        encoded = repetition_code.encode_bits(bits)
        decoded = repetition_code.decode_bits(encoded)

        assert decoded == bits

    def test_decode_majority_vote(self, repetition_code):
        noisy = '101'
        decoded = repetition_code.decode_bits(noisy) # Vote decoding should decide on 1
        assert decoded == '1'

    def test_repetition_r_is_odd(self):
        code = RepetitionChannelCode(r=3)
        assert code.r % 2 == 1

    def test_repetition_r_is_not_odd(self):
        with pytest.raises(ValueError):
            RepetitionChannelCode(r=4)

