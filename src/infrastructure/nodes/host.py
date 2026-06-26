from errors import ProtocolError
from infrastructure.nodes.node import Node
from src.protocol_stack.protocol_stack import ProtocolStack


class Host(Node):

    def __init__(self, cfg_manager, ip_address=None):
        super().__init__(ip_address)
        self.cfg_manager = cfg_manager
        self.protocol_stack = ProtocolStack(cfg_manager, address=self.address)
        self._rx_messages = []

    def send(self, message, interface_idx=0, destination_ip=None, destination_mac=None) -> None:
        top_layer = self.cfg_manager.top_layer

        if top_layer == 'physical':
            if interface_idx >= len(self.interfaces):
                raise ProtocolError('Requested interface does not exist')

            interface = self.interfaces[interface_idx]
            self._transmit(message, dst_ip=destination_ip,
                           src_mac=None, dst_mac=None, interface=interface)

        elif top_layer == 'link':
            if destination_mac is None:
                raise ProtocolError('Destination MAC is required')

            outgoing_interfaces = self._select_outgoing_interfaces(destination_mac)
            for interface in outgoing_interfaces:
                src_mac = interface.mac_address
                self._transmit(message, dst_ip=None,
                               src_mac=src_mac, dst_mac=destination_mac, interface=interface)

        else:  # network layer and above
            if destination_ip is None:
                raise ProtocolError('Destination IP is required')

            # TODO: when subnetworks are implemented,
            #  this could be improved to choose the correct interface instead of flooding
            for interface in self.interfaces:
                src_mac = interface.mac_address
                # TODO: resolve dst_mac via ARP
                self._transmit(message, dst_ip=destination_ip,
                               src_mac=src_mac, dst_mac=None, interface=interface)

    def _transmit(self, message, dst_ip, src_mac, dst_mac, interface):
        self.protocol_stack.transmit(message,
                                     interface=interface,
                                     destination_address=dst_ip,
                                     src_mac=src_mac,
                                     dst_mac=dst_mac)

    def on_receive(self, bits, interface=None) -> None:
        message = self.protocol_stack.on_receive(bits, interface)
        if message is not None:
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
