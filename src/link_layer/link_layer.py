import numpy as np

from src.link_layer.frame import Frame
from src.utils import int_to_bits, bits_to_int, pad_bits, unpad_bits
from numpy import typing as npt

from src.protocol_stack.layer import Layer


class LinkLayer(Layer):

    '''
        Current frame serializing protocol:
            -HEADER:
                >seq_size bits to represent sequence numbers
                >1 bit flag to mark if current frame is the last of a message
                >length to represent valid number of payload bits. By default log2(1 + payload_size)
            -PAYLOAD: payload_size bits to represent payload
            -TAIL: checksum_size bits to represent checksum
    '''

    def __init__(self, checksum, max_retries=5, payload_size=8, seq_size=8, checksum_size=4):
        self.checksum = checksum
        self.max_retries = max_retries
        self.payload_size = payload_size
        self.payload_length_field_size = np.ceil(np.log2(1 + payload_size)).astype(np.uint8)
        self.seq_size = seq_size
        self.checksum_size = checksum_size
        self._rx_buffer = []

    def _build_frames(self, bits):
        frames = []
        total_frames = (len(bits) + self.payload_size - 1) // self.payload_size
        for idx, i in enumerate(range(0, len(bits), self.payload_size)):
            seq = idx
            is_last = (idx == total_frames - 1)
            chunk = bits[i:i + self.payload_size]
            real_length = len(chunk)

            padded_payload = np.zeros(self.payload_size, dtype=np.uint8)
            padded_payload[:real_length] = chunk
            body = self._build_body(seq, is_last, real_length, padded_payload)

            cs = self._compute_checksum(body)
            frames.append(Frame(seq, is_last, real_length, padded_payload, cs))
        return frames

    def _build_body(self, seq, is_last, real_length, payload):
        seq_bits = int_to_bits(seq, self.seq_size)
        last_bit = np.array([is_last], dtype=np.uint8)
        real_length_bits = int_to_bits(real_length, self.payload_length_field_size)
        body = np.concatenate((seq_bits, last_bit, real_length_bits, payload))
        return body

    def _transmit_frame(self, frame, interface=None):
        bits = self._serialize_frame(frame)
        self.lower_layer.transmit(bits, interface)
        # raise LinkError('Maximum number of retries exceeded.', self.max_retries)

    # Main transmission method
    def transmit(self, bits, interface=None):
        frames = self._build_frames(bits)
        for frame in frames:
            self._transmit_frame(frame, interface)

    def on_receive(self, bits):
        frame = self._deserialize_frame(bits)
        self._rx_buffer.append(frame.get_true_payload())
        if frame.get_is_last():
            return self._rebuild_message()

    def _rebuild_message(self):
        message_bits = np.concatenate(self._rx_buffer)
        self._rx_buffer.clear()
        return self._forward_up(message_bits)

    def _serialize_frame(self, frame: Frame) -> npt.NDArray:
        seq_bits = int_to_bits(frame.get_seq(), self.seq_size)
        last_bit = np.array([frame.get_is_last()], dtype=np.uint8)
        real_length = int_to_bits(frame.get_real_length(), self.payload_length_field_size)

        payload = frame.get_payload()

        checksum = frame.get_checksum()
        return np.concatenate([seq_bits, last_bit, real_length, payload, checksum])

    def _deserialize_frame(self, received_bits: npt.NDArray) -> Frame:
        seq = bits_to_int(received_bits[:self.seq_size])
        is_last = received_bits[self.seq_size]

        real_length_field_start = self.seq_size + 1
        real_length_field_end = real_length_field_start + self.payload_length_field_size
        real_length = bits_to_int(received_bits[real_length_field_start : real_length_field_end])

        start = real_length_field_end
        end = start + self.payload_size
        padded_payload = received_bits[start:end]
        padding = len(padded_payload) - real_length
        payload = unpad_bits(padded_payload, padding)

        checksum = received_bits[-self.checksum_size:]

        frame = Frame(seq, is_last, real_length, payload, checksum)
        return frame

    def _compute_checksum(self, payload):
        raw_cs = self.checksum.compute(payload)
        if self.checksum.size > self.checksum_size:
            raise ValueError("Checksum is too large to be represented with these protocol settings")

        return pad_bits(raw_cs, self.checksum_size)[0]

    def _get_frame_size(self):
        return self.seq_size + 1 + self.payload_length_field_size + self.payload_size + self.checksum_size
