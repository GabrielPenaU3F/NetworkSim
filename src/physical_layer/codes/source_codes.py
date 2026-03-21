from abc import ABC, abstractmethod

import numpy as np


class SourceCode(ABC):

    @abstractmethod
    def build_codebook(self, alphabet):
        pass

    @abstractmethod
    def encode_bits(self, bits):
        pass

    @abstractmethod
    def decode_bits(self, bits):
        pass

class BasicSourceCode(SourceCode):

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

    def encode_bits(self, bits):
        return bits

    def decode_bits(self, bits):
        return bits
