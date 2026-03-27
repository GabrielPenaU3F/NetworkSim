from abc import abstractmethod, ABC

import numpy as np


class Checksum(ABC):

    @abstractmethod
    def compute(self, bits):
        pass

    @classmethod
    def validate(cls, params):
        pass


class ParityChecksum(Checksum):

    def compute(self, bits):
        return np.sum(bits) % 2


class SumChecksum(Checksum):

    def compute(self, bits):
        return np.sum(bits) % 256


class CRCChecksum:

    def __init__(self, crc_generator=np.array([1, 1, 0, 1])):
        self.generator = np.array(crc_generator, dtype=np.uint8)
        self.degree = len(crc_generator) - 1

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

    @classmethod
    def validate(cls, params):
        if 'crc_generator' not in params:
            raise ValueError("CRCChecksum requires 'generator'")

        g = np.array(params['crc_generator'])

        if g.ndim != 1 or len(g) < 2:
            raise ValueError("Generator must be 1D with length >= 2")

        if not np.all((g == 0) | (g == 1)):
            raise ValueError("Generator must contain only 0s and 1s")

        if g[0] != 1:
            raise ValueError("Generator must start with 1")

        if g[-1] != 1:
            raise ValueError("Generator must end with 1")
