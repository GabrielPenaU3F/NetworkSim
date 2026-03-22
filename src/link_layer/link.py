from src.errors import LinkError


class Link:

    def __init__(self, channel, checksum, block_size=8, max_retries=5):
        self.channel = channel
        self.checksum = checksum
        self.block_size = block_size
        self.max_retries = max_retries

    def split_blocks(self, bits):
        return [bits[i:i + self.block_size] for i in range(0, len(bits), self.block_size)]

    def transmit_block(self, bits):

        cs = self.checksum.compute(bits)
        for _ in range(self.max_retries):

            received_bits = self.channel.transmit(bits)
            if self.checksum.compute(received_bits) == cs:
                return received_bits

        raise LinkError('Maximum number of retries exceeded.', self.max_retries)

    def pad_bits(self, bits):
        padding = (self.block_size - len(bits) % self.block_size) % self.block_size
        return bits + '0' * padding, padding

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

            received_bits = ''.join(received_blocks)
            return self.unpad_bits(received_bits, padding)

        except LinkError:
            print('Transmission error. Closing link.')
