from abc import abstractmethod, ABC


class Layer(ABC):

    lower_layer = None

    def get_lower_layer(self):
        return self.lower_layer

    @abstractmethod
    def transmit(self, bits):
        pass
