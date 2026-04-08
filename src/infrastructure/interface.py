class Interface:

    def __init__(self, node, link):
        self.node = node
        self.link = link

    def send(self, bits):
        self.link.transmit(self, bits)

    def on_receive(self, bits):
        self.node.on_receive(bits)
