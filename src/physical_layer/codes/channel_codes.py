from abc import ABC, abstractmethod

import numpy as np


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
        return np.repeat(bits, self.r)

    def decode_bits(self, bits):
        bits = np.asarray(bits, dtype=np.uint8)
        n = len(bits) // self.r * self.r
        bits = bits[:n]
        blocks = bits.reshape(-1, self.r)
        ones = np.sum(blocks, axis=1)
        decoded = (ones > self.r/2).astype(np.uint8)
        return decoded


class HammingChannelCode(ChannelCode):

    # This may be improved in a (not near) future
    def __init__(self):
        self.data_bits = 4
        self.total_bits = 7

    def encode_bits(self, bits):
        bits = np.asarray(bits, dtype=np.uint8)

        # padding
        padding = (-len(bits)) % self.data_bits
        if padding > 0:
            bits = np.concatenate([bits, np.zeros(padding, dtype=np.uint8)])

        encoded_blocks = []

        for i in range(0, len(bits), self.data_bits):
            d = bits[i:i + 4]

            # syndromes
            p1 = d[0] ^ d[1] ^ d[3]
            p2 = d[0] ^ d[2] ^ d[3]
            p3 = d[1] ^ d[2] ^ d[3]

            block = np.array([p1, p2, d[0], p3, d[1], d[2], d[3]], dtype=np.uint8)
            encoded_blocks.append(block)

        return np.concatenate(encoded_blocks)

    def decode_bits(self, bits):
        bits = np.asarray(bits, dtype=np.uint8)

        decoded_blocks = []

        for i in range(0, len(bits), self.total_bits):
            block = bits[i:i + 7].copy()

            if len(block) < 7:
                continue

            # síndrome
            s1 = block[0] ^ block[2] ^ block[4] ^ block[6]
            s2 = block[1] ^ block[2] ^ block[5] ^ block[6]
            s3 = block[3] ^ block[4] ^ block[5] ^ block[6]

            error_pos = s1 + (s2 << 1) + (s3 << 2)

            if error_pos != 0:
                error_index = error_pos - 1
                block[error_index] ^= 1  # correct

            # datos
            data = block[[2, 4, 5, 6]]
            decoded_blocks.append(data)

        if not decoded_blocks:
            return np.array([], dtype=np.uint8)

        return np.concatenate(decoded_blocks)