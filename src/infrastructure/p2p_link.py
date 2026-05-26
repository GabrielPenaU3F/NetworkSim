class P2PLink:

    def __init__(self, iface_a, iface_b, channel):
        self.iface_a = iface_a
        self.iface_b = iface_b
        self.channel = channel

    def transmit(self, sender_interface, bits):
        noisy_bits = self.channel.apply_noise(bits)
        if sender_interface == self.iface_a:
            self.iface_b.on_receive(noisy_bits)
        else:
            self.iface_a.on_receive(noisy_bits)

    def get_interfaces(self):
        return self.iface_a, self.iface_b
