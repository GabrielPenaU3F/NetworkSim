import numpy as np
import logging
logger = logging.getLogger(__name__)

from src.errors import LinkError
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
                >1 bit flag to mark if current frame is an ACK frame
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
        self._rx_stream_buffer = []
        self._rx_message_buffer = []
        self._expected_seq = 0
        self._last_ack_seq = None

    def _build_frames(self, bits, is_ack=0):
        frames = []
        total_frames = (len(bits) + self.payload_size - 1) // self.payload_size
        for idx, i in enumerate(range(0, len(bits), self.payload_size)):
            seq = idx
            is_last = (idx == total_frames - 1)
            chunk = bits[i:i + self.payload_size]
            real_length = len(chunk)

            padded_payload = np.zeros(self.payload_size, dtype=np.uint8)
            padded_payload[:real_length] = chunk
            body = self._build_body(seq, is_last, is_ack, real_length, padded_payload)

            cs = self._compute_checksum(body)
            frames.append(Frame(seq, is_last, is_ack, real_length, padded_payload, cs))
        return frames

    def _build_body(self, seq, is_last, is_ack, real_length, payload):
        seq_bits = int_to_bits(seq, self.seq_size)
        is_last_bit = np.array([is_last], dtype=np.uint8)
        is_ack_bit = np.array([is_ack], dtype=np.uint8)
        real_length_bits = int_to_bits(real_length, self.payload_length_field_size)
        body = np.concatenate((seq_bits, is_last_bit, is_ack_bit, real_length_bits, payload))
        return body

    def _build_ack(self, seq):
        payload = np.zeros(self.payload_size, dtype=np.uint8)
        body = self._build_body(seq, is_last=0, is_ack=1, real_length=0, payload=payload)
        cs = self._compute_checksum(body)
        ack = Frame(seq=seq, is_last=0, is_ack=1, real_length=0, payload=payload, checksum=cs)
        return ack

    def _transmit_frame(self, frame, interface):
        bits = self._serialize_frame(frame)
        self.lower_layer.transmit(bits, interface)

    # Main transmission method
    def transmit(self, bits, interface, **kwargs):
        frames = self._build_frames(bits)
        for idx, frame in enumerate(frames):
            self._last_ack_seq = None
            retries = 0
            while not self._ack_received(frame) and retries < self.max_retries:
                self._transmit_frame(frame, interface)
                retries += 1

            if retries == self.max_retries:
                raise LinkError('Maximum number of retries exceeded.', self.max_retries)

    def on_receive(self, bits, interface=None):
        self._rx_stream_buffer.extend(bits)

        while len(self._rx_stream_buffer) >= self._get_frame_size():

            frame_bits = np.array(self._rx_stream_buffer[:self._get_frame_size()], dtype=np.uint8)
            self._rx_stream_buffer = self._rx_stream_buffer[self._get_frame_size():]

            if not self._validate_checksum(frame_bits):
                logger.debug("Checksum error → dropping frame")
                continue

            frame = self._deserialize_frame(frame_bits)
            if frame.is_ack:
                self._last_ack_seq = frame.seq
                continue

            # If it is a valid data frame, then send ack
            ack = self._build_ack(frame.seq)
            self._transmit_frame(ack, interface)

            if frame.seq == self._expected_seq:
                self._rx_message_buffer.append(frame.get_true_payload())
                self._expected_seq = (self._expected_seq + 1) % (2**self.seq_size)
                if frame.is_last:
                    return self._rebuild_message()

        return None

    def _rebuild_message(self):
        message_bits = np.concatenate(self._rx_message_buffer)
        self._clear_buffers()
        return self._forward_up(message_bits)

    def _clear_buffers(self):
        self._rx_stream_buffer.clear()
        self._rx_message_buffer.clear()

    def _serialize_frame(self, frame: Frame) -> npt.NDArray:
        seq_bits = int_to_bits(frame.seq, self.seq_size)
        is_last_bit = np.array([frame.is_last], dtype=np.uint8)
        is_ack_bit = np.array([frame.is_ack], dtype=np.uint8)
        real_length = int_to_bits(frame.real_length, self.payload_length_field_size)

        payload = frame.payload

        checksum = frame.checksum
        return np.concatenate([seq_bits, is_last_bit, is_ack_bit, real_length, payload, checksum])

    def _deserialize_frame(self, received_bits: npt.NDArray) -> Frame:
        seq = bits_to_int(received_bits[:self.seq_size])
        is_last = int(received_bits[self.seq_size])
        is_ack = int(received_bits[self.seq_size + 1])

        real_length_field_end = self._get_header_size()
        real_length_field_start = real_length_field_end - self.payload_length_field_size
        real_length = bits_to_int(received_bits[real_length_field_start : real_length_field_end])

        payload_start = real_length_field_end
        body_end = self._get_body_size()
        padded_payload = received_bits[payload_start:body_end]
        padding = len(padded_payload) - real_length
        payload = unpad_bits(padded_payload, padding)

        checksum = received_bits[body_end:]

        frame = Frame(seq, is_last, is_ack, real_length, payload, checksum)
        return frame

    def _validate_checksum(self, frame_bits):
        received_body = frame_bits[:self._get_body_size()]
        expected = self._compute_checksum(received_body)
        actual = frame_bits[-self.checksum_size:]
        return np.all(actual == expected)

    def _compute_checksum(self, body_bits):
        raw_cs = self.checksum.compute(body_bits)
        if self.checksum.size > self.checksum_size:
            raise ValueError("Checksum is too large to be represented with these protocol settings")

        return pad_bits(raw_cs, self.checksum_size)[0]

    def _ack_received(self, frame):
        return self._last_ack_seq == frame.seq

    def _get_frame_size(self):
        return self.seq_size + 2 + self.payload_length_field_size + self.payload_size + self.checksum_size

    def _get_header_size(self):
        return self.seq_size + 2 + self.payload_length_field_size

    def _get_body_size(self):
        return self.seq_size + 2 + self.payload_length_field_size + self.payload_size
