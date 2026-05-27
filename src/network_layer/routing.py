import numpy as np

from src.errors import NetworkError
from src.infrastructure.network_graph import NetworkGraph


class ShortestPathRouting:

    def __init__(self, graph: NetworkGraph):
        self.graph = graph
        self._cache = {}

    def get_first_hops(self, origin):
        if origin not in self._cache:
            self._cache[origin] = self._compute_first_hops(origin)
        return self._cache[origin]

    def _compute_first_hops(self, origin):

        # Initialization
        distances = self._initialize_distances(origin)
        predecessors = {}
        unvisited = set(self.graph.nodes)

        # Exploration
        while unvisited:

            # The current node is that of the least distance (first iteration is the origin node)
            current = min(unvisited, key=lambda node: distances[node])

            # If every node has infinity distance, then they are unreachable
            if current != origin and distances[current] == np.inf:
                raise NetworkError(f'Node {current.get_address()} is unreachable from {origin.get_address()}')

            # If it is reachable, we visit it
            unvisited.remove(current)

            # While visiting a node, we update the distance of each neighbor
            for neighbor in self.graph.get_neighbors(current):
                new_distance = distances[current] + 1
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current

        # Revisit backwards to find the first hop
        first_hops = {}
        for node in self.graph.nodes:
            if node == origin:
                continue
            first_hops[node] = self._get_first_hop(origin, node, predecessors)

        return first_hops

    def _initialize_distances(self, origin):
        distances = {node: np.inf for node in self.graph.nodes}
        distances[origin] = 0
        return distances

    def _get_first_hop(self, origin, destination, predecessors):
        # Seguimos los predecesores hacia atrás hasta llegar al origen
        current = destination
        while predecessors.get(current) != origin:
            current = predecessors.get(current)
            if current is None:
                return None  # destino no alcanzable
        return current
