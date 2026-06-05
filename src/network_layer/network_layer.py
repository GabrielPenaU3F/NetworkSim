import numpy as np

from src.network_layer.packets import IPPacket
from src.protocol_stack.layer import Layer
from numpy import typing as npt

from src.utils import serialize_ip_address, int_to_bits


class NetworkLayer(Layer):

    """
        Current network (IPv4-like) protocol:

            -HEADER:
                >packet_address_size bits to represent origin_address
                >packet_address_size bits to represent destination_address
                >1 bit flag to mark if current packet is the last of a message
                >offset_size bits to represent payload offset within the packet
            Thus header size is 2 x packet_address_size bits
            packet_address_size must be divisible by 16


            -PAYLOAD: packet_payload_size bits to represent payload
    """

    def __init__(self, address, address_size, offset_size, packet_payload_size):
        self.address = address
        self.address_size = address_size
        if self.address is not None:
            self.serialized_address = self._serialize_address()
        self.offset_size = offset_size
        self.packet_payload_size = packet_payload_size
        self.get_interface_for_address = None

    def transmit(self, bits, interface, destination_address='127.0.0.1', **kwargs):
        packets = self._build_packets(bits, destination_address)

    def on_receive(self, bits):
        pass

    def _build_packets(self, payload, destination_address):
        packets = []
        total = len(payload)
        for i, start in enumerate(range(0, total, self.packet_payload_size)):
            chunk = payload[start:start + self.packet_payload_size]
            is_last = int((start + self.packet_payload_size) >= total) # This is 1 if the message is complete
            offset = start

            padded_payload = np.zeros(self.packet_payload_size, dtype=np.uint8)
            padded_payload[:len(chunk)] = chunk

            packet = IPPacket(
                origin_address=self.address,
                destination_address=destination_address,
                offset=offset,
                is_last=is_last,
                payload=padded_payload
            )
            packets.append(packet)
        return packets

    def set_routing_callback(self, callback):
        self.get_interface_for_address = callback

    def _serialize_packet(self, packet: IPPacket) -> npt.NDArray:
        origin_address_bits = self.serialized_address
        destination_address_bits = serialize_ip_address(packet.destination_address, self.address_size)
        is_last_bit = np.array([packet.is_last], dtype=np.uint8)
        offset = int_to_bits(packet.offset, self.offset_size)
        payload = packet.payload

        return np.concatenate([origin_address_bits, destination_address_bits, is_last_bit, offset, payload])

    def _deserialize_packet(self, bits: np.ndarray) -> IPPacket:
        pass

    def _serialize_address(self):
        return serialize_ip_address(self.address, self.address_size)

