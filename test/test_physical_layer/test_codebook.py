import pytest

from src.physical_layer.alphabets.alphabets import AlphabetProvider
from src.physical_layer.codebook import Codebook

@pytest.fixture
def alphabet():
    return AlphabetProvider.provide_alphabet('test_16bits_alph')

@pytest.fixture
def codebook(alphabet):
    return Codebook(alphabet)


class TestCodebook:

    def test_codebook_size(self, codebook, alphabet):
        assert len(codebook.codebook) == len(alphabet)
        assert len(codebook.reverse_codebook) == len(alphabet)

    def test_bijection(self, codebook):
        for word, bits in codebook.codebook.items():
            assert codebook.reverse_codebook[bits] == word

    def test_word_length(self, codebook):
        lengths = [len(b) for b in codebook.codebook.values()]
        assert len(set(lengths)) == 1
        assert codebook.word_length == lengths[0]

    def test_unique_codes(self, codebook):
        codes = list(codebook.codebook.values())
        assert len(codes) == len(set(codes))

    def test_encode_message(self, codebook):
        message = "sol mar luz"
        bits = codebook.encode_message(message)

        expected = (
            codebook.codebook["sol"] +
            codebook.codebook["mar"] +
            codebook.codebook["luz"]
        )
        assert bits == expected

    def test_decode_message(self, codebook):
        words = ["sol", "mar", "luz"]
        bits = ''.join(codebook.codebook[w] for w in words)
        message = codebook.decode_message(bits)
        assert message == " ".join(words)

    def test_encode_decode_pipeline(self, codebook):
        message = "sol mar luz bosque"
        encoded = codebook.encode_message(message)
        decoded = codebook.decode_message(encoded)
        assert decoded == message

    def test_decode_unknown_code(self, codebook):
        invalid_bits = "111"
        decoded = codebook.decode_message(invalid_bits)
        assert "???" in decoded

    def test_decode_incomplete_bits(self, codebook):
        valid_bits = next(iter(codebook.codebook.values()))
        bits = valid_bits + "1"
        decoded = codebook.decode_message(bits)
        assert decoded.split()[-1] == "???"
