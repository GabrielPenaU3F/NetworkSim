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