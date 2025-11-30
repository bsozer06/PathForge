from typing import Dict, List, Tuple, Any
import json
import psycopg2
import os
from .heuristics import haversine

Graph = Dict[str, List[Dict[str, float]]]

class GraphBuilder:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('PGHOST', 'localhost'),
            port=os.getenv('PGPORT', '5432'),
            user=os.getenv('PGUSER', 'postgres'),
            password=os.getenv('PGPASSWORD', ''),
            dbname=os.getenv('PGDATABASE', 'osm')
        )
        self.graph: Graph = {}
        self.node_index: Dict[Tuple[float, float], str] = {}
        self.next_id = 0

    def _node_id(self, lat: float, lon: float) -> str:
        key = (lat, lon)
        if key in self.node_index:
            return self.node_index[key]
        nid = f"n{self.next_id}"
        self.next_id += 1
        self.node_index[key] = nid
        self.graph.setdefault(nid, [])
        return nid

    def build(self) -> Graph:
        cur = self.conn.cursor()
        # roads table is assumed; adjust as needed
        cur.execute("SELECT id, ST_AsGeoJSON(geom) FROM roads;")
        rows = cur.fetchall()
        for _rid, geojson in rows:
            data = json.loads(geojson)
            if data.get('type') != 'LineString':
                continue
            coords: List[List[float]] = data.get('coordinates', [])
            if len(coords) < 2:
                continue
            # Treat endpoints as nodes; simple MVP
            start = coords[0]
            end = coords[-1]
            lon1, lat1 = start
            lon2, lat2 = end
            a = self._node_id(lat1, lon1)
            b = self._node_id(lat2, lon2)
            dist = haversine(lat1, lon1, lat2, lon2)
            self.graph[a].append({'to': b, 'cost': dist})
            self.graph[b].append({'to': a, 'cost': dist})
        cur.close()
        return self.graph

    def close(self):
        self.conn.close()
