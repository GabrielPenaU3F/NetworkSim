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

    def __init__(self, checksum, max_retries=5, payload_size=8, seq_size=8, checksum_size=4):
        self.checksum = checksum
        self.max_retries = max_retries
        self.payload_size = payload_size
        self.seq_size = seq_size
        self.checksum_size = checksum_size
        self._rx_buffer = []

    def _build_frames(self, bits):
        frames = []
        total_frames = (len(bits) + self.payload_size - 1) // self.payload_size
        for idx, i in enumerate(range(0, len(bits), self.payload_size)):
            payload = bits[i:i + self.payload_size]
            seq = idx
            is_last = (idx == total_frames - 1)
            body = self._build_body(payload, seq, is_last)
            cs = self._compute_checksum(body)
            frames.append(Frame(payload, seq, cs, is_last))
        return frames

    def _build_body(self, payload, seq, is_last):
        seq_bits = int_to_bits(seq, self.seq_size)
        last_bit = np.array([is_last], dtype=np.uint8)
        body = np.concatenate((seq_bits, last_bit, payload))
        return body

    def _transmit_frame(self, frame, interface=None):
        bits = self._serialize_frame(frame)
        self.lower_layer.transmit(bits, interface)
        # raise LinkError('Maximum number of retries exceeded.', self.max_retries)

    # Main transmission method
    def transmit(self, bits, interface=None):
        bits, padding = pad_bits(bits, self.payload_size)
        frames = self._build_frames(bits)
        for frame in frames:
            self._transmit_frame(frame, interface)
            # received_bits = np.concatenate([frame.get_payload() for frame in received_frames])
            # unpadded = unpad_bits(received_bits, padding)

    def on_receive(self, bits):
        frame = self._deserialize_frame(bits)
        self._rx_buffer.append(frame.get_payload())
        if frame.get_is_last():
            return self._rebuild_message()

    def _rebuild_message(self):
        message_bits = np.concatenate(self._rx_buffer)
        self._rx_buffer.clear()
        return self._forward_up(message_bits)

    def _serialize_frame(self, frame: Frame) -> npt.NDArray:
        seq_bits = int_to_bits(frame.get_seq(), self.seq_size)
        last_bit = np.array([frame.get_is_last()], dtype=np.uint8)
        payload = frame.get_payload()
        checksum = frame.get_checksum()
        return np.concatenate([seq_bits, last_bit, payload, checksum])

    def _deserialize_frame(self, received_bits: npt.NDArray) -> Frame:
        seq = bits_to_int(received_bits[:self.seq_size])
        is_last = received_bits[self.seq_size]

        start = self.seq_size + 1
        end = start + self.payload_size
        payload = received_bits[start:end]

        checksum = received_bits[-self.checksum_size:]

        frame = Frame(payload, seq, checksum, is_last)
        return frame

    def _compute_checksum(self, payload):
        raw_cs = self.checksum.compute(payload)
        if self.checksum.size > self.checksum_size:
            raise ValueError("Checksum is too large to be represented with these protocol settings")

        return pad_bits(raw_cs, self.checksum_size)[0]

