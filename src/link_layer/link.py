import numpy as np

from src.communications_system.layer import Layer
from src.errors import LinkError


class Link(Layer):

    def __init__(self, physical_layer, checksum, block_size=8, max_retries=5):
        self.lower_layer = physical_layer
        self.checksum = checksum
        self.block_size = block_size
        self.max_retries = max_retries

    def split_blocks(self, bits):
        return [bits[i:i + self.block_size] for i in range(0, len(bits), self.block_size)]

    def transmit_block(self, bits):

        cs = self.checksum.compute(bits)
        for _ in range(self.max_retries):

            received_bits = self.lower_layer.transmit(bits)
            if self.checksum.compute(received_bits) == cs:
                return received_bits

        raise LinkError('Maximum number of retries exceeded.', self.max_retries)

    def pad_bits(self, bits):
        padding = (self.block_size - len(bits) % self.block_size) % self.block_size
        return np.concatenate([bits, np.zeros(padding, dtype=np.uint8)]), padding

    def unpad_bits(self, bits, padding):
        if padding == 0:
            return bits
        return bits[:-padding]

    # Main transmission method
    def transmit(self, bits):

        bits, padding = self.pad_bits(bits)
        blocks = self.split_blocks(bits)
        received_blocks = []

        try:
            for b in blocks:
                rb = self.transmit_block(b)
                received_blocks.append(rb)

            received_bits = np.array(received_blocks).reshape(-1)
            return self.unpad_bits(received_bits, padding)

        except LinkError:
            print('Transmission error. Closing link.')
