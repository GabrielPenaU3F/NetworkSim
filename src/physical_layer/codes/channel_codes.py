from abc import ABC, abstractmethod


class ChannelCode(ABC):

    @abstractmethod
    def encode_bits(self, bits):
        pass

    @abstractmethod
    def decode_bits(self, bits):
        pass


class NoChannelCode(ChannelCode):

    def encode_bits(self, bits):
        return bits

    def decode_bits(self, bits):
        return bits

class RepetitionChannelCode(ChannelCode):

    def __init__(self, r=3):
        self.r = r # Adjust as desired

    def encode_bits(self, bits):
        return ''.join(b * self.r for b in bits)

    def decode_bits(self, bits):
        decoded = ''
        for i in range(0, len(bits), self.r):
            chunk = bits[i:i+self.r]
            ones = chunk.count('1')
            zeros = chunk.count('0')
            decoded += '1' if ones > zeros else '0'
        return decoded