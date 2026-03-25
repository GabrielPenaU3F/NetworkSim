import numpy as np

from src.communications_system.layer import Layer
from src.errors import LinkError
from src.link_layer.frame import Frame
from src.physical_layer.utils import int_to_bits


class Link(Layer):

    def __init__(self, physical_layer, checksum, block_size=8, max_retries=5):
        self.lower_layer = physical_layer
        self.checksum = checksum
        self.block_size = block_size
        self.max_retries = max_retries

    def build_frames(self, bits):
        frames = []
        for i in range(0, len(bits), self.block_size):
            payload = bits[i:i + self.block_size]
            seq = i // self.block_size
            cs = self.checksum.compute(payload)
            frames.append(Frame(payload, seq, cs))
        return frames

    def transmit_frame(self, frame):

        for _ in range(self.max_retries):

            bits = self.serialize(frame)
            received_bits = self.lower_layer.transmit(bits)
            if self.checksum.compute(received_bits) == frame.get_checksum():
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
        frames = self.build_frames(bits)
        received_frames = []
        try:
            for frame in frames:
                rf = self.transmit_frame(frame)
                received_frames.append(rf)

            received_bits = np.array(received_frames).reshape(-1)
            return self.unpad_bits(received_bits, padding)

        except LinkError:
            print('Transmission error. Closing link.')

    def serialize(self, frame):
        seq_bits = int_to_bits(frame.get_seq(), self.seq_bits)
        payload = frame.get_payload()
        checksum = frame.get_checksum()
        return np.concatenate([seq_bits, payload, checksum])
