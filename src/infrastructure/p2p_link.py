from src.infrastructure.interface import Interface


class P2PLink:

    def __init__(self, node_a, node_b, channel):
        self.iface_a = Interface(node_a, self)
        self.iface_b = Interface(node_b, self)
        self.channel = channel

        node_a.add_interface(self.iface_a)
        node_b.add_interface(self.iface_b)

    def transmit(self, sender_interface, bits):
        noisy_bits = self.channel.apply_noise(bits)
        if sender_interface == self.iface_a:
            self.iface_b.on_receive(noisy_bits)
        else:
            self.iface_a.on_receive(noisy_bits)
