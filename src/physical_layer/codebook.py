import numpy as np

from src.physical_layer.codes import BasicCode


class Codebook:

    available_codes = {
        'basic': BasicCode
    }
    alphabet = []
    codebook = []
    reverse_codebook = []

    def __init__(self, alphabet, code='basic'):
        self.alphabet = alphabet
        code = self.available_codes[code]()
        self.codebook, self.reverse_codebook = code.build_codebook(alphabet)
        self.word_length = len(next(iter(self.codebook.values()))) # Valid only if every codeword has the same length

    def analyze_code(self):
        codes = list(self.codebook.values())
        codes_int = np.array([int(code, 2) for code in codes], dtype=np.uint32)
        n = len(codes_int)
        min_dist = np.inf

        for i in range(n):
            xor = codes_int[i] ^ codes_int[i + 1:]
            # contar bits en 1
            dists = np.bitwise_count(xor)
            if xor.size > 0:
                min_dist = min(min_dist, dists.min())

        print(f'Minimum distance: {min_dist}')

    def print_codebook(self):
        print('Word -- Code')
        for word in self.alphabet:
            print(f'{word}: {self.codebook[word]}')

    def get_word_length(self):
        return self.word_length

    def get_codebook(self):
        return self.codebook

    def get_reverse_codebook(self):
        return self.reverse_codebook
