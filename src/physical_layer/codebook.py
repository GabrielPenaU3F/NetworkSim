import numpy as np

from src.physical_layer.codes.source_codes import BasicSourceCode


class Codebook:

    # These must be source codes
    available_codes = {
        'basic': BasicSourceCode,
    }
    alphabet = []
    codebook = []
    reverse_codebook = []

    def __init__(self, alphabet, code='basic'):
        self.alphabet = alphabet
        self.code = self.available_codes[code]()
        self.codebook, self.reverse_codebook = self.code.build_codebook(alphabet)
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

    def encode_message(self, message):
        split_msg = message.split(' ')
        bits = ''.join(self.codebook[word] for word in split_msg)
        encoded_bits = self.code.encode_bits(bits)
        return encoded_bits

    def decode_message(self, message):
        bits = self.code.decode_bits(message)
        len_word = self.word_length
        words = []
        for i in range(0, len(bits), len_word):
            word_bits = bits[i:i+len_word]
            word = self.reverse_codebook.get(word_bits, '???')
            words.append(word)
        return ' '.join(words)
