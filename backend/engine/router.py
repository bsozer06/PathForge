from typing import Dict, List, Tuple, Optional
import heapq
from .heuristics import haversine

Edge = Dict[str, float]
Graph = Dict[str, List[Edge]]

class Router:
    def __init__(self, graph: Graph, node_index: Dict[Tuple[float, float], str]):
        self.graph = graph
        self.node_index = node_index
        # reverse index for coordinates retrieval
        self.rev_index = {v: k for k, v in node_index.items()}

    def _nearest_node(self, lat: float, lon: float) -> Optional[str]:
        # Simple linear search; optimize later
        best = None
        best_d = float('inf')
        for nid, (nlat, nlon) in self.rev_index.items():
            d = haversine(lat, lon, nlat, nlon)
            if d < best_d:
                best_d = d
                best = nid
        return best

    def route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> List[Tuple[float, float]]:
        start_id = self._nearest_node(start_lat, start_lon)
        end_id = self._nearest_node(end_lat, end_lon)
        if not start_id or not end_id:
            return []

        open_set = []
        heapq.heappush(open_set, (0, start_id))
        came_from: Dict[str, str] = {}
        g: Dict[str, float] = {start_id: 0.0}
        f: Dict[str, float] = {start_id: haversine(*self.rev_index[start_id], end_lat, end_lon)}
        closed = set()

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end_id:
                return self._reconstruct(came_from, current)
            closed.add(current)
            for edge in self.graph.get(current, []):
                neighbor = edge['to']
                tentative_g = g[current] + edge['cost']
                if neighbor in closed and tentative_g >= g.get(neighbor, float('inf')):
                    continue
                if tentative_g < g.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g[neighbor] = tentative_g
                    f[neighbor] = tentative_g + haversine(*self.rev_index[neighbor], end_lat, end_lon)
                    heapq.heappush(open_set, (f[neighbor], neighbor))
        return []

    def _reconstruct(self, came_from: Dict[str, str], current: str) -> List[Tuple[float, float]]:
        path = [self.rev_index[current]]
        while current in came_from:
            current = came_from[current]
            path.append(self.rev_index[current])
        path.reverse()
        return path
