class Interface:

    def __init__(self, node):
        self.edge = None
        self.link = None
        self.node = node

    def send(self, bits):
        self.link.transmit(self, bits)

    def on_receive(self, bits):
        self.node.on_receive(bits, self) # inject RX interface

    def attach_link(self, link):
        self.link = link

    def connect_edge(self, edge):
        self.edge = edge
