from abc import abstractmethod, ABC


class Checksum(ABC):

    @abstractmethod
    def compute(self, bits):
        pass


class ParityChecksum(Checksum):

    def compute(self, bits):
        return sum(int(b) for b in bits) % 2


class SumChecksum(Checksum):

    def compute(self, bits):
        return sum(int(b) for b in bits) % 256


class CRCChecksum:

    def __init__(self, generator="1101"):
        self.generator = generator
        self.degree = len(generator) - 1

    def compute(self, bits):
        padded = bits + '0' * self.degree
        remainder = self._mod2div(padded)
        return remainder

    def _mod2div(self, dividend):
        divisor = self.generator
        n = len(divisor)
        remainder = list(dividend)

        for i in range(len(dividend) - n + 1):
            if remainder[i] == '1':
                for j in range(n):
                    remainder[i + j] = str(
                        int(remainder[i + j]) ^ int(divisor[j])
                    )

        return ''.join(remainder[-self.degree:])