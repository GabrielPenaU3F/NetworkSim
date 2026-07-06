from typing import Any

from errors import ProtocolError
from infrastructure.nodes.node import Node
from network_layer.packets import ARPPacket
from protocol_constants import arp
from src.protocol_stack.protocol_stack import ProtocolStack


class Host(Node):

    def __init__(self, cfg_manager, ip_address=None):
        super().__init__(ip_address)
        self.cfg_manager = cfg_manager
        self._protocol_stack = ProtocolStack(cfg_manager, ip_address=self.ip_address)
        self._rx_messages = []
        self._pending_messages = {}  # {dst_ip: [(message, interface)]}

    def send(self, message, interface_idx=0, dst_ip=None, dst_mac=None) -> None:
        top_layer = self.cfg_manager.top_layer

        if top_layer == 'physical':
            if interface_idx >= len(self.interfaces):
                raise ProtocolError('Requested interface does not exist')

            interface = self.interfaces[interface_idx]
            self._transmit(message, dst_ip=dst_ip,
                           src_mac=None, dst_mac=None, interface=interface)

        elif top_layer == 'link':
            if dst_mac is None:
                raise ProtocolError('Destination MAC is required')

            outgoing_interfaces = self._select_outgoing_interfaces(dst_mac)
            for interface in outgoing_interfaces:
                src_mac = interface.mac_address
                self._transmit(message, dst_ip=None,
                               src_mac=src_mac, dst_mac=dst_mac, interface=interface)

        else:  # network layer and above
            if dst_ip is None:
                raise ProtocolError('Destination IP is required')

            # TODO: when subnetworks are implemented,
            #  this could be improved to choose the correct interface instead of flooding
            for interface in self.interfaces:
                src_mac = interface.mac_address
                dst_mac = self._get_mac_for_ip(dst_ip)

                if dst_mac is not None:
                    self._transmit(message, dst_ip=dst_ip,
                                   src_mac=src_mac, dst_mac=dst_mac, interface=interface)

                else:
                    # Cache the message and send ARP request
                    if dst_ip not in self._pending_messages:
                        self._pending_messages[dst_ip] = []

                    self._pending_messages[dst_ip].append((message, interface))  # primero cachear
                    if len(self._pending_messages[dst_ip]) == 1:  # solo enviar ARP la primera vez
                        self._send_arp_request(dst_ip=dst_ip, interface=interface)

    def _get_mac_for_ip(self, dst_ip):
        return self._protocol_stack.get_dst_mac_from_arp_cache(dst_ip)

    def _transmit(self, message, dst_ip, src_mac, dst_mac, interface):
        self._protocol_stack.transmit(message,
                                      interface=interface,
                                      dst_ip=dst_ip,
                                      src_mac=src_mac,
                                      dst_mac=dst_mac)

    def on_receive(self, bits, interface=None) -> None:
        message = self._protocol_stack.on_receive(bits, interface)
        if message is None:
            return

        if isinstance(message, ARPPacket):
            if message.operation == arp.ARP_REPLY:
                self._flush_pending_messages(message.sender_ip, message.sender_mac)
        else:
            self._rx_messages.append(message)

    def read(self):
        if self._rx_messages:
            return self._rx_messages.pop(0)

    def _select_outgoing_interfaces(self, destination_mac):
        # First: check if destination is a direct neighbor
        for interface in self.interfaces:
            other_interface = interface.get_other_interface()
            if other_interface.mac_address == destination_mac:
                return [interface]

        # Otherwise: flood to all interfaces
        return self.interfaces

    def _send_arp_request(self, dst_ip, interface):
        self._protocol_stack.send_arp_request(dst_ip=dst_ip, interface=interface)

    def _flush_pending_messages(self, dst_ip, dst_mac):
        pending = self._pending_messages.pop(dst_ip, [])
        for message, interface in pending:
            self._transmit(message, dst_ip=dst_ip,
                           src_mac=interface.mac_address,
                           dst_mac=dst_mac, interface=interface)

        self._pending_messages = {}
