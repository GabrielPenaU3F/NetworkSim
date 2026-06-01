from dataclasses import dataclass


class NetworkGraph:

    def __init__(self):
        self.nodes = []
        self._adjacency = {}
        self._observers = []

    def node_count(self):
        return len(self.nodes)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
            self._adjacency[node] = []
        self._notify_change()

    def add_edge(self, node_a, node_b, link=None):
        if self.get_edge_to(node_a, node_b) is not None:
            raise ValueError('An edge between these nodes already exists')

        edge = Edge(node_a, node_b, link)
        self._adjacency[node_a].append(edge)
        self._adjacency[node_b].append(edge)
        self._notify_change()
        return edge

    def get_neighbors(self, node):
        return [edge.get_other_node(node) for edge in self._adjacency[node]]

    def get_edge_to(self, node, neighbor):
        for edge in self._adjacency[node]:
            if edge.get_other_node(node) == neighbor:
                return edge
        return None

    def subscribe(self, observer):
        self._observers.append(observer)

    def _notify_change(self):
        for observer in self._observers:
            observer.on_graph_changed()


# noinspection PyUnresolvedReferences
@dataclass
class Edge:

    node_a: 'Node' = None
    node_b: 'Node' = None
    link: 'P2PLink' = None

    def get_other_node(self, node):
        if self.node_a == node:
            return self.node_b
        return self.node_a

    def get_interface_for(self, node):
        return node.get_interface_for_edge(self)
