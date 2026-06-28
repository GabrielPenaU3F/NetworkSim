import numpy as np

from numpy import typing as npt
from network_layer.packets import IPPacket
from utils import int_to_bits, serialize_ip_address, deserialize_ip_address, bits_to_int

"""
    Current network (IPv4-style) protocol, but with fixed payload length:

        -HEADER:
            >packet_address_size bits to represent origin_address
            >packet_address_size bits to represent destination_address
            >1 bit flag to mark if current packet is the last of a message
            >offset_size bits to represent payload offset within the packet
            >real_length_size bits to represent payload length

        packet_address_size must be divisible by 16

        -PAYLOAD: packet_payload_size bits to represent payload
"""
class IPModule:

    def __init__(self, ip, address_size, offset_size, real_length_size, packet_payload_size):
        self.ip = ip
        self.address_size = address_size
        self.num_parts = self.address_size // 8
        self.offset_size = offset_size
        self.real_length_size = real_length_size
        self.packet_payload_size = packet_payload_size

    def build_packets(self, payload, destination_address):
        packets = []
        total = len(payload)
        for i, start in enumerate(range(0, total, self.packet_payload_size)):
            chunk = payload[start:start + self.packet_payload_size]
            is_last = int((start + self.packet_payload_size) >= total) # This is 1 if the message is complete
            offset = start
            real_length = len(chunk)

            padded_payload = np.zeros(self.packet_payload_size, dtype=np.uint8)
            padded_payload[:len(chunk)] = chunk

            packet = IPPacket(
                origin_address=self.ip,
                destination_address=destination_address,
                is_last=is_last,
                offset=offset,
                real_length=real_length,
                payload=padded_payload
            )
            packets.append(packet)
        return packets

    def serialize_packet(self, packet: IPPacket) -> npt.NDArray:
        origin_address_bits = serialize_ip_address(packet.origin_address, self.address_size)
        destination_address_bits = serialize_ip_address(packet.destination_address, self.address_size)
        is_last_bit = np.array([packet.is_last], dtype=np.uint8)
        offset = int_to_bits(packet.offset, self.offset_size)
        real_length = int_to_bits(packet.real_length, self.real_length_size)
        payload = packet.payload

        return np.concatenate([origin_address_bits, destination_address_bits, is_last_bit, offset, real_length, payload])

    def deserialize_packet(self, received_bits: np.ndarray) -> IPPacket:
        origin_address = deserialize_ip_address(received_bits[:self.address_size], self.num_parts)
        destination_end = 2 * self.address_size
        destination_address = deserialize_ip_address(received_bits[self.address_size: destination_end], self.num_parts)
        is_last = int(received_bits[destination_end])

        offset_start = destination_end + 1
        offset_end = offset_start + self.offset_size
        offset = bits_to_int(received_bits[offset_start: offset_end])

        real_length = bits_to_int(received_bits[offset_end: offset_end + self.real_length_size])
        payload = received_bits[-self.packet_payload_size:]

        packet = IPPacket(origin_address, destination_address, is_last, offset, real_length, payload)
        return packet

    def offsets_are_contiguous(self, offset_a, offset_b):
        return offset_b == offset_a + self.packet_payload_size

    def packet_is_for_me(self, destination_ip):
        return destination_ip == self.ip
