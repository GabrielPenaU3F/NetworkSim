class NetworkGraph:

    def __init__(self):
        self.nodes = []
        self._adjacency = {}

    def node_count(self):
        return len(self.nodes)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
            self._adjacency[node] = []

    def add_edge(self, node_a, node_b):
        if node_a not in self.nodes or node_b not in self.nodes:
            raise ValueError('Cannot create an edge between nonexistent nodes')
        self._adjacency[node_a].append(node_b)
        self._adjacency[node_b].append(node_a)

    def get_neighbors(self, node):
        return self._adjacency[node]
