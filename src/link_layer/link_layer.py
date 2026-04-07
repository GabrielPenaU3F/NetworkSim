import numpy as np


from src.errors import LinkError
from src.link_layer.frame import Frame
from src.physical_layer.utils import int_to_bits, bits_to_int
from numpy import typing as npt

from src.protocol_stack.layer import Layer


def pad_bits(bits, size):
    padding = (size - len(bits) % size) % size
    return np.concatenate([bits, np.zeros(padding, dtype=np.uint8)]), padding


def unpad_bits(bits, padding):
    if padding == 0:
        return bits
    return bits[:-padding]


class LinkLayer(Layer):

    '''
        Current frame serializing protocol:
            -HEADER: seq_size bits to represent sequence numbers
            -PAYLOAD: payload_size bits to represent payload
            -TAIL: checksum_size bits to represent checksum
    '''

    def __init__(self, physical_layer, checksum, max_retries=5, payload_size=8, seq_size=8, checksum_size=4):
        self.checksum = checksum
        self.lower_layer = physical_layer
        self.max_retries = max_retries
        self.payload_size = payload_size
        self.seq_size = seq_size
        self.checksum_size = checksum_size

    def build_frames(self, bits):
        frames = []
        for i in range(0, len(bits), self.payload_size):
            payload = bits[i:i + self.payload_size]
            seq = i // self.payload_size
            body = self._build_body(payload, seq)
            cs = self._compute_checksum(body)
            frames.append(Frame(payload, seq, cs))
        return frames

    def _build_body(self, payload, seq):
        seq_bits = int_to_bits(seq, self.seq_size)
        body = np.concatenate((seq_bits, payload))
        return body

    def transmit_frame(self, frame):

        for _ in range(self.max_retries):

            bits = self._serialize_frame(frame)
            received_bits = self.lower_layer.transmit(bits)
            received_body = received_bits[:self.seq_size + self.payload_size]
            if np.all(self._compute_checksum(received_body) == frame.get_checksum()):
                received_frame = self._deserialize_frame(received_bits)
                return received_frame

        raise LinkError('Maximum number of retries exceeded.', self.max_retries)

    # Main transmission method
    def transmit(self, bits):

        bits, padding = pad_bits(bits, self.payload_size)
        frames = self.build_frames(bits)
        received_frames = []
        try:
            for frame in frames:
                rf = self.transmit_frame(frame)
                received_frames.append(rf)

            received_bits = np.concatenate([frame.get_payload() for frame in received_frames])
            return unpad_bits(received_bits, padding)

        except LinkError:
            print('Transmission error. Closing link.')

    def _serialize_frame(self, frame: Frame) -> npt.NDArray:
        seq_bits = int_to_bits(frame.get_seq(), self.seq_size)
        payload = frame.get_payload()
        checksum = frame.get_checksum()
        return np.concatenate([seq_bits, payload, checksum])

    def _deserialize_frame(self, received_bits: npt.NDArray) -> Frame:
        seq = bits_to_int(received_bits[:self.seq_size])
        payload = received_bits[self.seq_size:self.seq_size + self.payload_size]
        checksum = received_bits[-self.checksum_size:]
        frame = Frame(payload, seq, checksum)
        return frame

    def _compute_checksum(self, payload):
        raw_cs = self.checksum.compute(payload)
        if self.checksum.size > self.checksum_size:
            raise ValueError("Checksum is too large to be represented with these protocol settings")

        return pad_bits(raw_cs, self.checksum_size)[0]

