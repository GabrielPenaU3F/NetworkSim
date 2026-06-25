from errors import NetworkError, LinkError, ProtocolError, AddressError
from infrastructure.nodes.node import Node
from src.protocol_stack.protocol_stack import ProtocolStack


class Host(Node):

    def __init__(self, cfg_manager, address=None):
        super().__init__(address)
        self.cfg_manager = cfg_manager
        self.protocol_stack = ProtocolStack(cfg_manager, address=self.address)
        self._rx_messages = []

    def send(self, message, interface_idx=0, destination_ip=None, destination_mac=None) -> None:
        top_layer = self.cfg_manager.top_layer

        if top_layer == 'physical':
            if interface_idx >= len(self.interfaces):
                raise ProtocolError('Requested interface does not exist')

            src_mac, dst_mac = None, None
            interface = self.interfaces[interface_idx]

        elif top_layer == 'link':
            if destination_mac is None:
                raise ProtocolError('Destination MAC is required')

            interface = self._select_interface_for_mac(destination_mac)
            src_mac = interface.mac_address
            dst_mac = destination_mac

        else:  # network layer and above
            if destination_ip is None:
                raise ProtocolError('Destination IP is required')

            if self.routing_table is None:
                raise NetworkError('Routing tables have not been built')

            interface = self.routing_table.get_interface_to_address(destination_ip)
            src_mac = interface.mac_address
            dst_mac = interface.link.get_other_interface(interface).mac_address

        self.protocol_stack.transmit(message, interface,
                                     destination_address=destination_ip,
                                     src_mac=src_mac,
                                     dst_mac=dst_mac)

    def on_receive(self, bits, interface=None) -> None:
        message = self.protocol_stack.on_receive(bits, interface)
        if message is not None:
            self._rx_messages.append(message)

    def read(self):
        if self._rx_messages:
            return self._rx_messages.pop(0)

    def _select_interface_for_mac(self, destination_mac):
        for interface in self.interfaces:
            other_interface = interface.get_other_interface()
            if other_interface.mac_address == destination_mac:
                return interface

        raise AddressError('Destination MAC is not connected to this host')
