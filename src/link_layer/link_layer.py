import numpy as np

from link_layer.ether_frame import EthernetFrame
from protocol_constants import ethernet
from protocol_stack.layer import Layer
from utils import int_to_bits, deserialize_mac_address, bits_to_int


class LinkLayer(Layer):


    def __init__(self):
        super().__init__()

    def _build_frames(self, bits, src_mac, dst_mac, ether_type):
        frames = []
        total = len(bits)

        for start in range(0, total, ethernet.MAX_PAYLOAD_BITS):
            chunk = bits[start:start + ethernet.MAX_PAYLOAD_BITS]
            real_length = len(chunk)

            if real_length < ethernet.MIN_PAYLOAD_BITS:
                padding = np.zeros(ethernet.MIN_PAYLOAD_BITS - real_length, dtype=np.uint8)
                chunk = np.concatenate([chunk, padding])

            frame = EthernetFrame(
                src_mac=src_mac,
                dst_mac=dst_mac,
                ether_type=ether_type,
                real_length=real_length,
                payload=chunk
            )
            frames.append(frame)

        return frames

    def transmit(self, bits, interface, **kwargs):
        interface.send(bits)

    def on_receive(self, bits, interface=None):
        return self._forward_up(bits, interface)

    def _serialize_frame(self, ether_frame) -> np.ndarray:
        body_bits = ether_frame.serialize_body()
        checksum_bits = int_to_bits(ether_frame.checksum, ethernet.CHECKSUM_SIZE)

        return np.concatenate([body_bits, checksum_bits])

    def _deserialize_frame(self, bits: np.ndarray, payload_size: int) -> EthernetFrame:
        dst_mac = deserialize_mac_address(bits[:ethernet.MAC_SIZE])

        src_start = ethernet.MAC_SIZE
        src_end = src_start + ethernet.MAC_SIZE
        src_mac = deserialize_mac_address(bits[src_start:src_end])

        ether_type_end = src_end + ethernet.ETHER_TYPE_SIZE
        ether_type = bits_to_int(bits[src_end:ether_type_end])

        real_length_end = ether_type_end + ethernet.REAL_LENGTH_SIZE
        real_length = bits_to_int(bits[ether_type_end:real_length_end])

        payload_end = real_length_end + payload_size
        payload = bits[real_length_end:payload_end]

        '''
        The real checksum - need to compare
        checksum = bits_to_int(bits[payload_end:payload_end + ethernet.CHECKSUM_SIZE])
        '''
        return EthernetFrame(src_mac=src_mac, dst_mac=dst_mac, ether_type=ether_type,
                   real_length=real_length, payload=payload)
