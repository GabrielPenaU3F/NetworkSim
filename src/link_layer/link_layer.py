import numpy as np
import logging

from protocol_constants import ethernet

logger = logging.getLogger(__name__)

from link_layer.link_module import LinkModule
from protocol_stack.layer import Layer


class LinkLayer(Layer):

    def __init__(self, checksum, min_payload_bits, max_payload_bits,
                 mac_size, ether_type_size, real_length_size, checksum_size):
        super().__init__()
        self._link_module = LinkModule(
            checksum, min_payload_bits, max_payload_bits, mac_size, ether_type_size,
            real_length_size, checksum_size)
        self._rx_stream_buffer = []
        self._rx_message_buffer = []

    def _build_frames(self, bits, src_mac, dst_mac, ether_type):
        frames = []
        total = len(bits)

        for start in range(0, total, self._link_module.max_payload_bits):
            chunk = bits[start:start + self._link_module.max_payload_bits]
            real_length = len(chunk)

            if real_length < self._link_module.min_payload_bits:
                padding = np.zeros(self._link_module.min_payload_bits - real_length, dtype=np.uint8)
                chunk = np.concatenate([chunk, padding])

            frame = self._link_module.build_frame(src_mac, dst_mac, ether_type, real_length, chunk)
            frames.append(frame)

        return frames

    def transmit(self, bits, interface, src_mac=None, dst_mac=None, ether_type=ethernet.IPV4, **kwargs):
        frames = self._build_frames(bits, src_mac, dst_mac, ether_type)
        for frame in frames:
            serialized = self._link_module.serialize_frame(frame)
            self.lower_layer.transmit(serialized, interface)

    def on_receive(self, bits, interface=None):
        self._rx_stream_buffer.extend(bits)

        while True:
            if len(self._rx_stream_buffer) < self._link_module.header_size:
                break

            header_bits = np.array(self._rx_stream_buffer[:self._link_module.header_size], dtype=np.uint8)
            real_length = self._link_module.peek_real_length(header_bits)
            wire_payload_size = int(max(real_length, self._link_module.min_payload_bits))
            frame_size = self._link_module.header_size + wire_payload_size + self._link_module.checksum_size

            if len(self._rx_stream_buffer) < frame_size:
                break  # not enough bits yet for the full frame

            frame_bits = np.array(self._rx_stream_buffer[:frame_size], dtype=np.uint8)
            self._rx_stream_buffer = self._rx_stream_buffer[frame_size:]

            frame = self._link_module.deserialize_frame(frame_bits, wire_payload_size)

            if not self._link_module.validate_checksum(frame_bits):
                logger.debug("Checksum error → dropping frame")
                continue

            self._rx_message_buffer.append(frame.payload[:frame.real_length])

            if frame.real_length < self._link_module.max_payload_bits:
                return self._rebuild_message()

        return None

    def _rebuild_message(self):
        message = np.concatenate(self._rx_message_buffer)
        self._clear_buffers()
        return self._forward_up(message)

    def _clear_buffers(self):
        self._rx_stream_buffer.clear()
        self._rx_message_buffer.clear()
