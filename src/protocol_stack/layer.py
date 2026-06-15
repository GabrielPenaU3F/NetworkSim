from abc import abstractmethod, ABC

from src.errors import ProtocolError


class Layer(ABC):

    lower_layer = None
    upper_layer = None

    def _forward_up(self, bits, interface=None):
        if self.upper_layer is not None:
            return self.upper_layer.on_receive(bits, interface)

        return bits

    def attach_lower(self, lower):
        if self.lower_layer is not None:
            raise ProtocolError("Upper layer already connected")
        if lower.upper_layer is not None:
            raise ProtocolError("Lower layer already connected")
        self.lower_layer = lower
        lower.upper_layer = self

    @abstractmethod
    def transmit(self, bits, interface, **kwargs):
        pass

    @abstractmethod
    def on_receive(self, bits, interface=None):
        pass
