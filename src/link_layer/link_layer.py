from protocol_stack.layer import Layer


class LinkLayer(Layer):

    def transmit(self, bits, interface, **kwargs):
        interface.send(bits)

    def on_receive(self, bits, interface=None):
        return self._forward_up(bits, interface)
