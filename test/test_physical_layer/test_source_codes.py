import pytest
import numpy as np

from src.physical_layer.alphabets.alphabets import AlphabetProvider
from src.physical_layer.codes.source_codes import BasicSourceCode


@pytest.fixture
def alphabet():
    return AlphabetProvider.provide_alphabet('test_16bits_alph')


@pytest.fixture
def basic_source_code():
    return BasicSourceCode()

class TestBasicSourceCode:

    # 🔹 Test 1: codebook size
    def test_codebook_size(self, basic_source_code, alphabet):
        codebook, reverse = basic_source_code.build_codebook(alphabet)

        assert len(codebook) == len(alphabet)
        assert len(reverse) == len(alphabet)


    # 🔹 Test 2: every symbol is present
    def test_all_symbols_present(self, basic_source_code, alphabet):
        codebook, _ = basic_source_code.build_codebook(alphabet)

        for word in alphabet:
            assert word in codebook


    # 🔹 Test 3: unique codes
    def test_unique_codes(self, basic_source_code, alphabet):
        codebook, _ = basic_source_code.build_codebook(alphabet)

        codes = list(codebook.values())
        assert len(codes) == len(set(codes))


    # 🔹 Test 4: correct length
    def test_code_length(self, basic_source_code, alphabet):
        codebook, _ = basic_source_code.build_codebook(alphabet)

        n_bits = int(np.ceil(np.log2(len(alphabet))))

        for code in codebook.values():
            assert len(code) == n_bits


    # 🔹 Test 5: consistency
    def test_reverse_mapping(self, basic_source_code, alphabet):
        codebook, reverse = basic_source_code.build_codebook(alphabet)

        for word, code in codebook.items():
            assert reverse[code] == word


    # 🔹 Test 6: encode_bits should be identity
    def test_encode_bits_identity(self, basic_source_code):
        bits = "0101011100"
        assert basic_source_code.encode_bits(bits) == bits


    # 🔹 Test 7: decode_bits should be identity
    def test_decode_bits_identity(self, basic_source_code):
        bits = "1110001010"
        assert basic_source_code.decode_bits(bits) == bits


    # 🔹 Test 8: encode + decode (pipeline)
    def test_encode_decode_pipeline(self, basic_source_code):
        bits = "0101010101110001"
        encoded = basic_source_code.encode_bits(bits)
        decoded = basic_source_code.decode_bits(encoded)

        assert decoded == bits