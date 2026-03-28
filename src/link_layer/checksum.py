from abc import abstractmethod, ABC
from numpy import typing as npt

import numpy as np

from src.physical_layer.utils import int_to_bits


class Checksum(ABC):

    @abstractmethod
    def compute(self, bits) -> npt.NDArray[np.uint8]:
        pass

    @property
    @abstractmethod
    def size(self):
        pass

    @classmethod
    def validate(cls, params):
        pass


class ParityChecksum(Checksum):

    def compute(self, bits) -> npt.NDArray[np.uint8]:
        cs = np.sum(bits) % 2
        return np.array([cs], dtype=np.uint8)

    @property
    def size(self):
        return 1


class SumChecksum(Checksum):

    def compute(self, bits):
        cs = np.sum(bits) % 256
        cs = int_to_bits(cs, self.size)
        return np.array(cs, dtype=np.uint8)

    @property
    def size(self):
        return 8


class CRCChecksum(Checksum):

    def __init__(self, crc_generator=np.array([1, 1, 0, 1])):
        self.generator = np.array(crc_generator, dtype=np.uint8)
        self.degree = len(crc_generator) - 1

    def compute(self, bits):
        padded = np.concatenate([bits, np.zeros(self.degree, dtype=np.uint8)])
        remainder = self._mod2div(padded).astype(np.uint8)
        return remainder[-self.degree:]

    @property
    def size(self):
        return self.degree

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
