class Interface:

    def __init__(self, node, link):
        self.edge = None
        self.node = node
        self.link = link

    def send(self, bits):
        self.link.transmit(self, bits)

    def on_receive(self, bits):
        self.node.on_receive(bits, self) # inject RX interface

    def connect_edge(self, edge):
        self.edge = edge
