from abc import ABC, abstractmethod

import numpy as np


class Code(ABC):

    @abstractmethod
    def build_codebook(self, alphabet):
        pass

    @abstractmethod
    def select_binary_format(self, alphabet):
        pass


class BasicCode(Code):

    def build_codebook(self, alphabet):
        codebook = {}
        reverse = {}
        binary_format = self.select_binary_format(alphabet)
        for i, word in enumerate(alphabet):
            bits = format(i, binary_format)  # The word index is the bit-code
            codebook[word] = bits
            reverse[bits] = word

        return codebook, reverse

    def select_binary_format(self, alphabet):
        n = len(alphabet)
        n_bits = int(np.ceil(np.log2(n)))
        return f'0{n_bits}b'


class RepetitionCode(Code):

    def __init__(self, r=3):
        self.r = r # Adjust as desired

    def build_codebook(self, alphabet):
        base = BasicCode()
        codebook, reverse = base.build_codebook(alphabet)

        new_codebook = {}
        new_reverse = {}

        for word, bits in codebook.items():
            encoded = ''.join(b * self.r for b in bits)
            new_codebook[word] = encoded
            new_reverse[encoded] = word

        return new_codebook, new_reverse

    def select_binary_format(self, alphabet):
        pass  # no aplica