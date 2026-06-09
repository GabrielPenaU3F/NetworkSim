import numpy as np

from src.network_layer.packets import IPPacket
from src.protocol_stack.layer import Layer
from numpy import typing as npt

from src.utils import serialize_ip_address, int_to_bits, deserialize_ip_address, bits_to_int


class NetworkLayer(Layer):

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
    get_interface_for_address = lambda x: None

    def __init__(self, address, address_size, offset_size, real_length_size, packet_payload_size):
        self.address = address
        self.address_size = address_size
        self.num_parts = self.address_size // 8
        self.offset_size = offset_size
        self.real_length_size = real_length_size
        self.packet_payload_size = packet_payload_size
        self.get_interface_for_address = lambda x: None
        self._rx_buffer = {}  # { offset: (payload, real_length) }
        self._last_received = False

    def transmit(self, bits, interface, destination_address='127.0.0.1', **kwargs):
        packets = self._build_packets(bits, destination_address)
        for idx, packet in enumerate(packets):
            self._transmit_packet(interface, packet)

    def _transmit_packet(self, interface, packet):
        bits = self._serialize_packet(packet)
        self.lower_layer.transmit(bits, interface)

    def on_receive(self, bits, interface=None):
        packet = self._deserialize_packet(bits)

        if not packet.destination_address == self.address:
            interface = self.get_interface_for_address(packet.destination_address)
            self._transmit_packet(interface, packet)
            return None

        self._rx_buffer[packet.offset] = (packet.payload, packet.real_length)
        if packet.is_last:
            self._last_received = True

        if self._last_received and self._message_complete():
            return self._rebuild_message()

        return None

    def _build_packets(self, payload, destination_address):
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
                origin_address=self.address,
                destination_address=destination_address,
                is_last=is_last,
                offset=offset,
                real_length=real_length,
                payload=padded_payload
            )
            packets.append(packet)
        return packets

    def set_routing_callback(self, callback):
        self.get_interface_for_address = callback

    def _serialize_packet(self, packet: IPPacket) -> npt.NDArray:
        origin_address_bits = serialize_ip_address(packet.origin_address, self.address_size)
        destination_address_bits = serialize_ip_address(packet.destination_address, self.address_size)
        is_last_bit = np.array([packet.is_last], dtype=np.uint8)
        offset = int_to_bits(packet.offset, self.offset_size)
        real_length = int_to_bits(packet.real_length, self.real_length_size)
        payload = packet.payload

        return np.concatenate([origin_address_bits, destination_address_bits, is_last_bit, offset, real_length, payload])

    def _deserialize_packet(self, received_bits: np.ndarray) -> IPPacket:
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

    # Returns true if the buffer contains no holes
    def _message_complete(self):
        offsets = sorted(self._rx_buffer.keys())

        if not offsets:
            return False

        if offsets[0] != 0:  # message must begin in 0 - if not, then the message is incomplete
            return False

        for i, offset in enumerate(offsets):
            if i > 0 and offset != offsets[i - 1] + self.packet_payload_size:
                return False

        return True

    def _rebuild_message(self):
        offsets = sorted(self._rx_buffer.keys())
        trimmed_buffer = [self._trim_payload(offset) for offset in offsets]
        message = np.concatenate(trimmed_buffer)
        self._clear_buffers()
        return self._forward_up(message)

    def _clear_buffers(self):
        self._rx_buffer.clear()
        self._last_received = False

    def _trim_payload(self, offset):
        payload, real_length = self._rx_buffer[offset]
        return payload[:real_length]
