import numpy as np

from src.link_layer.ether_frame import EthernetFrame
from src.utils import serialize_mac_address, deserialize_mac_address, int_to_bits, bits_to_int


class LinkModule:

    def __init__(self, checksum, min_payload_bits, max_payload_bits,
                 mac_size, ether_type_size, real_length_size, checksum_size):
        self.checksum = checksum
        self.min_payload_bits = min_payload_bits
        self.max_payload_bits = max_payload_bits
        self.mac_size = mac_size
        self.ether_type_size = ether_type_size
        self.real_length_size = real_length_size
        self.checksum_size = checksum_size
        self.header_size = mac_size * 2 + ether_type_size + real_length_size

    def build_frame(self, src_mac, dst_mac, ether_type, real_length, payload):
        body = self._build_body(src_mac, dst_mac, ether_type, real_length, payload)
        checksum = self.compute_checksum(body)
        return EthernetFrame(src_mac, dst_mac, ether_type, real_length, payload, checksum)

    def serialize_frame(self, frame: EthernetFrame) -> np.ndarray:
        body = self._build_body(frame.src_mac, frame.dst_mac, frame.ether_type,
                                 frame.real_length, frame.payload)
        checksum_bits = int_to_bits(frame.checksum, self.checksum_size)
        return np.concatenate([body, checksum_bits])

    def deserialize_frame(self, bits: np.ndarray, payload_size: int) -> EthernetFrame:
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

        return EthernetFrame(src_mac, dst_mac, ether_type, real_length, payload, checksum)

    def peek_next_frame_size(self, buffer_bits):
        if len(buffer_bits) < self.header_size:
            return None

        header_bits = np.array(buffer_bits[:self.header_size], dtype=np.uint8)
        real_length = self.peek_real_length(header_bits)
        wire_payload_size = int(max(real_length, self.min_payload_bits))
        return self.header_size + wire_payload_size + self.checksum_size

    def validate_checksum(self, frame_bits):
        body_size = len(frame_bits) - self.checksum_size
        body = frame_bits[:body_size]
        expected = self.compute_checksum(body)
        actual = bits_to_int(frame_bits[body_size:])
        return actual == expected

    def peek_real_length(self, header_bits):
        real_length_end = self.header_size
        real_length_start = real_length_end - self.real_length_size
        return bits_to_int(header_bits[real_length_start:real_length_end])

    def _build_body(self, src_mac, dst_mac, ether_type, real_length, payload):
        dst_bits = serialize_mac_address(dst_mac, self.mac_size)
        src_bits = serialize_mac_address(src_mac, self.mac_size)
        ether_type_bits = int_to_bits(ether_type, self.ether_type_size)
        real_length_bits = int_to_bits(real_length, self.real_length_size)
        return np.concatenate([dst_bits, src_bits, ether_type_bits, real_length_bits, payload])

    def compute_checksum(self, body_bits):
        raw_cs = self.checksum.compute(body_bits)
        return bits_to_int(raw_cs)