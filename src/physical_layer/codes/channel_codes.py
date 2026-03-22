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
        if r % 2 == 0:
            raise ValueError("Repetition factor must be odd")
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


class HammingChannelCode(ChannelCode):

    # This may be improved in a (not near) future
    def __init__(self):
        self.data_bits = 4
        self.total_bits = 7

    def encode_bits(self, bits):
        encoded = ""
        padding = (-len(bits)) % self.data_bits
        bits = bits + '0' * padding
        for i in range(0, len(bits), self.data_bits):
            d = [int(b) for b in bits[i:i + 4]]

            # Positions:
            # p1 p2 d1 p3 d2 d3 d4
            p1 = d[0] ^ d[1] ^ d[3]
            p2 = d[0] ^ d[2] ^ d[3]
            p3 = d[1] ^ d[2] ^ d[3]

            block = [p1, p2, d[0], p3, d[1], d[2], d[3]]
            encoded += ''.join(str(b) for b in block)

        return encoded

    def decode_bits(self, bits):
        decoded = ""
        for i in range(0, len(bits), self.total_bits):
            block = [int(b) for b in bits[i:i + 7]]
            if len(block) < 7:
                continue

            # syndrome
            s1 = block[0] ^ block[2] ^ block[4] ^ block[6]
            s2 = block[1] ^ block[2] ^ block[5] ^ block[6]
            s3 = block[3] ^ block[4] ^ block[5] ^ block[6]

            error_pos = s1 + (s2 << 1) + (s3 << 2)
            if error_pos != 0:
                error_index = error_pos - 1
                block[error_index] ^= 1  # correct

            # extract actual data
            data = [block[2], block[4], block[5], block[6]]
            decoded += ''.join(str(b) for b in data)

        return decoded