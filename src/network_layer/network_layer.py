import numpy as np
import logging

from network_layer.network_modules.ip_module import IPModule

logger = logging.getLogger(__name__)

from src.protocol_stack.layer import Layer


class NetworkLayer(Layer):


    def __init__(self, ip, address_size, offset_size, real_length_size, packet_payload_size):
        self.ip_module = IPModule(ip, address_size, offset_size, real_length_size, packet_payload_size)
        self._rx_buffer = {}  # { offset: (payload, real_length) }
        self._last_received = False

    def transmit(self, bits, interface, dst_ip='127.0.0.1', dst_mac=None, **kwargs):
        packets = self.ip_module.build_packets(bits, dst_ip)
        for idx, packet in enumerate(packets):
            self._transmit_packet(packet, interface, dst_mac)

    def _transmit_packet(self, packet, interface, dst_mac):
        if dst_mac is None:
            logger.debug("No destination MAC available, dropping packet")
            return

        bits = self.ip_module.serialize_packet(packet)
        # This should be improved when we have ARP and MAC resolution available
        src_mac = interface.mac_address
        self.lower_layer.transmit(bits, interface, src_mac=src_mac, dst_mac=dst_mac)

    def on_receive(self, bits, interface=None):
        packet = self.ip_module.deserialize_packet(bits)

        if not self.ip_module.packet_is_for_me(packet.destination_address):
            logger.debug(f"Packet for {packet.destination_address} discarded (not for this node)")
            return None

        self._rx_buffer[packet.offset] = (packet.payload, packet.real_length)
        if packet.is_last:
            self._last_received = True

        if self._last_received and self._message_complete():
            return self._rebuild_message()

        return None

    # Returns true if the buffer contains no holes
    def _message_complete(self):
        offsets = sorted(self._rx_buffer.keys())

        if not offsets:
            return False

        if offsets[0] != 0:  # message must begin in 0 - if not, then the message is incomplete
            return False

        for i, offset in enumerate(offsets):
            if i > 0 and not self.ip_module.offsets_are_contiguous(offsets[i-1], offset):
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
