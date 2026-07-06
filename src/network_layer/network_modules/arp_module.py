import logging
import numpy as np

from network_layer.packets import ARPPacket
from protocol_constants import arp
from utils import serialize_mac_address, serialize_ip_address, deserialize_mac_address, deserialize_ip_address

logger = logging.getLogger(__name__)


class ARPModule:

    def __init__(self, mac_address_size, ip_address_size):
        self.mac_address_size = mac_address_size
        self.ip_address_size = ip_address_size
        self.num_parts = ip_address_size // 8
        self._arp_cache = {} # {ip: mac}'

    def serialize_packet(self, packet: ARPPacket) -> np.ndarray:
        operation_bit = np.array([packet.operation], dtype=np.uint8)
        sender_mac_bits = serialize_mac_address(packet.sender_mac, self.mac_address_size)
        sender_ip_bits = serialize_ip_address(packet.sender_ip, self.ip_address_size)
        target_mac_bits = serialize_mac_address(packet.target_mac, self.mac_address_size)
        target_ip_bits = serialize_ip_address(packet.target_ip, self.ip_address_size)

        return np.concatenate([
            operation_bit,
            sender_mac_bits,
            sender_ip_bits,
            target_mac_bits,
            target_ip_bits
        ])

    def deserialize_packet(self, bits: np.ndarray) -> ARPPacket:
        operation = int(bits[0])

        sender_mac_end = 1 + self.mac_address_size
        sender_mac = deserialize_mac_address(bits[1:sender_mac_end])

        sender_ip_end = sender_mac_end + self.ip_address_size
        sender_ip = deserialize_ip_address(bits[sender_mac_end:sender_ip_end], self.num_parts)

        target_mac_end = sender_ip_end + self.mac_address_size
        target_mac = deserialize_mac_address(bits[sender_ip_end:target_mac_end])

        target_ip_end = target_mac_end + self.ip_address_size
        target_ip = deserialize_ip_address(bits[target_mac_end:target_ip_end], self.num_parts)

        return ARPPacket(
            operation=operation,
            sender_mac=sender_mac,
            sender_ip=sender_ip,
            target_mac=target_mac,
            target_ip=target_ip
        )

    def handle_incoming_packet(self, bits, my_ip, my_mac):
        packet = self.deserialize_packet(bits)
        if packet.target_ip != my_ip:
            logger.debug(f"Packet for {packet.target_ip} discarded (not for this node)")
            return None  # It is not for this node

        self._arp_cache[packet.sender_ip] = packet.sender_mac # update cache
        if packet.operation == arp.ARP_REQUEST:
            return self._build_reply(packet, my_mac)

        elif packet.operation == arp.ARP_REPLY:
            return None

    def _build_reply(self, packet, my_mac):
        reply_packet = ARPPacket(
            operation=arp.ARP_REPLY,
            sender_mac=my_mac,
            sender_ip=packet.target_ip, # this is my IP
            target_mac=packet.sender_mac,
            target_ip=packet.sender_ip
        )
        return reply_packet
