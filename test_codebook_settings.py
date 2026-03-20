# Test alphabet
from alphabets.alphabets import AlphabetProvider
from src.physical_layer.codebook import Codebook

def make_test_codebook(code='basic'):
    alphabet = AlphabetProvider.provide_alphabet('test_16bits_alph')
    return Codebook(alphabet, code)

if __name__ == "__main__":
    codebook = make_test_codebook()
    codebook.analyze_code()
