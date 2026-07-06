import numpy as np
import logging

from network_layer.network_modules.arp_module import ARPModule, ARP_ACTION_REPLY_RECEIVED
from network_layer.network_modules.ip_module import IPModule
from network_layer.packets import ARPPacket
from protocol_constants import arp, ethernet, ip
from src.protocol_stack.layer import Layer

logger = logging.getLogger(__name__)



class NetworkLayer(Layer):

    def __init__(self, ip_address, address_size, offset_size, real_length_size, packet_payload_size):
        self._ip_module = IPModule(ip_address, address_size, offset_size, real_length_size, packet_payload_size)
        self._arp_module = ARPModule(ethernet.MAC_SIZE, ip.IP_SIZE)
        self._rx_buffer = {}  # { offset: (payload, real_length) }
        self._last_received = False

    def transmit(self, bits, interface, dst_ip='127.0.0.1', dst_mac=None, **kwargs):
        packets = self._ip_module.build_packets(bits, dst_ip)
        for idx, packet in enumerate(packets):
            self._transmit_packet(packet, interface, dst_mac)

    def _transmit_packet(self, packet, interface, dst_mac):
        if dst_mac is None:
            logger.debug("No destination MAC available, dropping packet")
            return

        bits = self._ip_module.serialize_packet(packet)
        # This should be improved when we have ARP and MAC resolution available
        self.lower_layer.transmit(bits, interface,
                                  src_mac=interface.mac_address, dst_mac=dst_mac, ether_type=packet.ether_type)

    def on_receive(self, bits, interface=None, **kwargs):
        ether_type = kwargs.get('ether_type', ethernet.IPV4)
        if ether_type == ethernet.IPV4:
            return self._handle_incoming_ip_packet(bits)

        elif ether_type == ethernet.ARP:
            return self._handle_incoming_arp_packet(bits, interface)

        return None

    def get_dst_mac_from_arp_cache(self, dst_ip):
        return self._arp_module._arp_cache.get(dst_ip)

    def _handle_incoming_ip_packet(self, bits):
        packet = self._ip_module.handle_incoming_packet(bits)
        if packet is None:
            return None
        self._rx_buffer[packet.offset] = (packet.payload, packet.real_length)
        if packet.is_last:
            self._last_received = True
        if self._last_received and self._message_complete():
            return self._rebuild_message()
        return None

    def _handle_incoming_arp_packet(self, bits, interface=None):
        result = self._arp_module.handle_incoming_packet(bits, self._ip_module.ip, interface.mac_address)
        if result is None:
            logger.debug("Discarding ARP packet, not for this node")
            return None

        action, packet = result
        if action == ARP_ACTION_REPLY_RECEIVED:
            return packet  # return it to the host

        # If it is a REQUEST: send reply
        reply_bits = self._arp_module.serialize_packet(packet)
        self.lower_layer.transmit(reply_bits, interface,
                                  src_mac=interface.mac_address,
                                  dst_mac=packet.target_mac,
                                  ether_type=ethernet.ARP)
        return None

    def send_arp_request(self, target_ip, interface):
        packet = ARPPacket(
            operation=arp.ARP_REQUEST,
            sender_mac=interface.mac_address,
            sender_ip=self._ip_module.ip,
            target_mac='00:00:00:00:00:00',
            target_ip=target_ip
        )
        bits = self._arp_module.serialize_packet(packet)
        self.lower_layer.transmit(bits, interface,
                                  src_mac=interface.mac_address,
                                  dst_mac=ethernet.BROADCAST_MAC,
                                  ether_type=ethernet.ARP)

    # Returns true if the buffer contains no holes
    def _message_complete(self):
        offsets = sorted(self._rx_buffer.keys())

        if not offsets:
            return False

        if offsets[0] != 0:  # message must begin in 0 - if not, then the message is incomplete
            return False

        for i, offset in enumerate(offsets):
            if i > 0 and not self._ip_module.offsets_are_contiguous(offsets[i-1], offset):
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
