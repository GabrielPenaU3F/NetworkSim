from abc import abstractmethod, ABC


class Layer(ABC):

    lower_layer = None
    upper_layer = None

    def _forward_up(self, bits, interface=None):
        if self.upper_layer is not None:
            return self.upper_layer.on_receive(bits, interface)

        return bits

    @abstractmethod
    def transmit(self, bits, interface=None):
        pass

    @abstractmethod
    def on_receive(self, bits, interface=None):
        pass
