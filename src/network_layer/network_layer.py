import numpy as np

from src.network_layer.packets import IPPacket
from src.protocol_stack.layer import Layer


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

    def __init__(self, address, address_size, packet_payload_size):
        self.address = address
        self.address_size = address_size
        self.packet_payload_size = packet_payload_size

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