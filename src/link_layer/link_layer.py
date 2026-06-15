import numpy as np

from link_layer.ether_frame import EthernetFrame
from protocol_stack.layer import Layer
from utils import serialize_mac_address, int_to_bits, deserialize_mac_address, bits_to_int


class LinkLayer(Layer):

    def __init__(self, mac_size=48, ethernet_type_size=16, checksum_size=32):
        self.MAC_SIZE = mac_size
        self.ETHER_TYPE_SIZE = ethernet_type_size
        self.CHECKSUM_SIZE = checksum_size

    def transmit(self, bits, interface, **kwargs):
        interface.send(bits)

    def on_receive(self, bits, interface=None):
        return self._forward_up(bits, interface)

    def _serialize_frame(self, ether_frame) -> np.ndarray:
        dst_bits = serialize_mac_address(ether_frame.dst_mac, self.MAC_SIZE)
        src_bits = serialize_mac_address(ether_frame.src_mac, self.MAC_SIZE)
        ether_type_bits = int_to_bits(ether_frame.ether_type, self.ETHER_TYPE_SIZE)
        checksum_bits = int_to_bits(ether_frame.checksum, self.CHECKSUM_SIZE)

        return np.concatenate([dst_bits, src_bits, ether_type_bits, ether_frame.payload, checksum_bits])

    def _deserialize_frame(self, bits: np.ndarray, payload_size: int) -> EthernetFrame:
        dst_mac = deserialize_mac_address(bits[:self.MAC_SIZE])

        src_start = self.MAC_SIZE
        src_end = src_start + self.MAC_SIZE
        src_mac = deserialize_mac_address(bits[src_start:src_end])

        ether_type_end = src_end + self.ETHER_TYPE_SIZE
        ether_type = bits_to_int(bits[src_end:ether_type_end])

        payload_end = ether_type_end + payload_size
        payload = bits[ether_type_end:payload_end]

        checksum = bits_to_int(bits[payload_end:payload_end + self.CHECKSUM_SIZE])

        return EthernetFrame(src_mac=src_mac, dst_mac=dst_mac, ether_type=ether_type,
                   payload=payload, checksum=checksum)
