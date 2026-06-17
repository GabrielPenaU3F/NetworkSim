import numpy as np
import logging

logger = logging.getLogger(__name__)

from link_layer.ether_frame import EthernetFrame
from protocol_constants.ethernet import IPV4
from protocol_stack.layer import Layer
from utils import int_to_bits, deserialize_mac_address, bits_to_int, serialize_mac_address


class LinkLayer(Layer):

    def __init__(self, checksum, min_payload_bits, max_payload_bits,
                 mac_size, ether_type_size, real_length_size, checksum_size):
        super().__init__()
        self.checksum = checksum
        self.min_payload_bits = min_payload_bits
        self.max_payload_bits = max_payload_bits
        self.mac_size = mac_size
        self.ether_type_size = ether_type_size
        self.real_length_size = real_length_size
        self.checksum_size = checksum_size
        self.header_size = mac_size * 2 + ether_type_size + real_length_size
        self._rx_stream_buffer = []
        self._rx_message_buffer = []

    def _build_frames(self, bits, src_mac, dst_mac, ether_type):
        frames = []
        total = len(bits)

        for start in range(0, total, self.max_payload_bits):
            chunk = bits[start:start + self.max_payload_bits]
            real_length = len(chunk)

            if real_length < self.min_payload_bits:
                padding = np.zeros(self.min_payload_bits - real_length, dtype=np.uint8)
                chunk = np.concatenate([chunk, padding])

            body = self._build_body(src_mac, dst_mac, ether_type, real_length, chunk)
            cs = self._compute_checksum(body)

            frame = EthernetFrame(
                src_mac=src_mac,
                dst_mac=dst_mac,
                ether_type=ether_type,
                real_length=real_length,
                payload=chunk,
                checksum=cs
            )
            frames.append(frame)

        return frames

    def transmit(self, bits, interface, src_mac=None, dst_mac=None, ether_type=IPV4, **kwargs):
        frames = self._build_frames(bits, src_mac, dst_mac, ether_type)
        for frame in frames:
            serialized = self._serialize_frame(frame)
            self.lower_layer.transmit(serialized, interface)

    def on_receive(self, bits, interface=None):
        self._rx_stream_buffer.extend(bits)

        while True:
            if len(self._rx_stream_buffer) < self.header_size:
                break

            header_bits = np.array(self._rx_stream_buffer[:self.header_size], dtype=np.uint8)
            real_length = self._peek_real_length(header_bits)
            wire_payload_size = int(max(real_length, self.min_payload_bits))
            frame_size = self.header_size + wire_payload_size + self.checksum_size

            if len(self._rx_stream_buffer) < frame_size:
                break  # not enough bits yet for the full frame

            frame_bits = np.array(self._rx_stream_buffer[:frame_size], dtype=np.uint8)
            self._rx_stream_buffer = self._rx_stream_buffer[frame_size:]

            frame = self._deserialize_frame(frame_bits, wire_payload_size)

            if not self._validate_checksum(frame_bits):
                logger.debug("Checksum error → dropping frame")
                continue

            self._rx_message_buffer.append(frame.payload[:frame.real_length])

            if frame.real_length < self.max_payload_bits:
                return self._rebuild_message()

        return None

    def _serialize_frame(self, ether_frame) -> np.ndarray:
        body_bits = self._build_body(ether_frame.src_mac, ether_frame.dst_mac, ether_frame.ether_type,
                                     ether_frame.real_length, ether_frame.payload)
        checksum_bits = int_to_bits(ether_frame.checksum, self.checksum_size)

        return np.concatenate([body_bits, checksum_bits])

    def _deserialize_frame(self, bits: np.ndarray, payload_size: int) -> EthernetFrame:
        dst_mac = deserialize_mac_address(bits[:self.mac_size])

        src_start = self.mac_size
        src_end = src_start + self.mac_size
        src_mac = deserialize_mac_address(bits[src_start:src_end])

        ether_type_end = src_end + self.ether_type_size
        ether_type = bits_to_int(bits[src_end:ether_type_end])

        real_length_end = ether_type_end + self.real_length_size
        real_length = bits_to_int(bits[ether_type_end:real_length_end])

        payload_end = real_length_end + payload_size
        payload = bits[real_length_end:payload_end]

        checksum = bits_to_int(bits[payload_end:])

        return EthernetFrame(src_mac=src_mac, dst_mac=dst_mac, ether_type=ether_type,
                   real_length=real_length, payload=payload, checksum=checksum)

    def _peek_real_length(self, header_bits):
        real_length_end = self.header_size
        real_length_start = real_length_end - self.real_length_size
        return bits_to_int(header_bits[real_length_start:real_length_end])

    def _rebuild_message(self):
        message = np.concatenate(self._rx_message_buffer)
        self._clear_buffers()
        return self._forward_up(message)

    def _clear_buffers(self):
        self._rx_stream_buffer.clear()
        self._rx_message_buffer.clear()

    def _build_body(self, src_mac, dst_mac, ether_type, real_length, payload):
        dst_bits = serialize_mac_address(dst_mac, self.mac_size)
        src_bits = serialize_mac_address(src_mac, self.mac_size)
        ether_type_bits = int_to_bits(ether_type, self.ether_type_size)
        real_length_bits = int_to_bits(real_length, self.real_length_size)
        return np.concatenate([dst_bits, src_bits, ether_type_bits, real_length_bits, payload])

    def _compute_checksum(self, body_bits):
        raw_cs = self.checksum.compute(body_bits)
        return bits_to_int(raw_cs)

    def _validate_checksum(self, frame_bits):
        body_size = len(frame_bits) - self.checksum_size
        body = frame_bits[:body_size]
        expected = self._compute_checksum(body)
        actual = bits_to_int(frame_bits[body_size:])
        return actual == expected