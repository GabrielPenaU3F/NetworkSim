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

    # Temporal method - will be erased later when it is not needed anymore
    def get_other_interface(self, interface):
        if interface == self.iface_a:
            return self.iface_b
        return self.iface_a