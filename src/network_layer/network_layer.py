from src.protocol_stack.layer import Layer


class NetworkLayer(Layer):

    def transmit(self, bits, interface, destination_address='127.0.0.1', **kwargs):
        pass

    def on_receive(self, bits):
        pass