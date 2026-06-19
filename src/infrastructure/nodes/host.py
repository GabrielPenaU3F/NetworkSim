from errors import NetworkError, LinkError
from infrastructure.nodes.node import Node
from src.protocol_stack.protocol_stack import ProtocolStack


class Host(Node):

    def __init__(self, cfg_manager, address=None):
        super().__init__(address)
        self.cfg_manager = cfg_manager
        self.protocol_stack = ProtocolStack(cfg_manager, address=self.address)
        self._rx_messages = []

    def send(self, message, interface_idx=0, destination_address=None) -> None:
        if self.cfg_manager.top_layer in ['physical', 'link']:
            self.check_if_interface_is_connected(interface_idx)
        
        if destination_address is not None: # if we are in network layer or above
            if self.routing_table is None:
                raise NetworkError('Routing tables have not been built')
            interface = self.routing_table.get_interface_to_address(destination_address)
        else: # if we are in physical or link layer
            interface = self.interfaces[interface_idx]
        self.protocol_stack.transmit(message, interface, destination_address=destination_address)

    def on_receive(self, bits, interface=None) -> None:
        message = self.protocol_stack.on_receive(bits, interface)
        if message is not None:
            self._rx_messages.append(message)

    def read(self):
        if self._rx_messages:
            return self._rx_messages.pop(0)

    def check_if_interface_is_connected(self, interface):
        if not self.interfaces or interface >= len(self.interfaces):
            raise LinkError('Destination interface is not connected')
