from src.protocol_stack.layer import Layer


class NetworkLayer(Layer):

    """
        Current network (IPv4-like) protocol:

            -HEADER:
                >packet_address_size bits to represent origin_address
                >packet_address_size bits to represent destination_address
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
        pass