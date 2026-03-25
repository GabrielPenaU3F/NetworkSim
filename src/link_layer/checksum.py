from abc import abstractmethod, ABC

import numpy as np


class Checksum(ABC):

    @abstractmethod
    def compute(self, bits):
        pass


class ParityChecksum(Checksum):

    def compute(self, bits):
        return np.sum(bits) % 2


class SumChecksum(Checksum):

    def compute(self, bits):
        return np.sum(bits) % 256


class CRCChecksum:

    def __init__(self, generator=np.array([1, 1, 0, 1])):
        self.generator = np.array(generator, dtype=np.uint8)
        self.degree = len(generator) - 1

    def compute(self, bits):
        padded = np.concatenate([bits, np.zeros(self.degree, dtype=np.uint8)])
        remainder = self._mod2div(padded)
        return remainder

    def _mod2div(self, dividend):
        divisor = self.generator
        n = len(divisor)
        remainder = dividend.copy()
        for i in range(len(dividend) - n + 1):
            if remainder[i] == 1:
                remainder[i:i + n] ^= divisor

        return remainder