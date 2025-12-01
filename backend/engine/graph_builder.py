from typing import Dict, List, Tuple, Any
import json
import psycopg2
import os
import pickle
from pathlib import Path
from .heuristics import haversine

Graph = Dict[str, List[Dict[str, float]]]

class GraphBuilder:
    def __init__(self):
        self.graph: Graph = {}
        self.node_index: Dict[Tuple[float, float], str] = {}
        self.next_id = 0
        self._cache_path = Path(os.getenv('GRAPH_CACHE_PATH', 'backend/data/graph_cache.pkl'))
        self._conn = None

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
        # Check if 'roads' table exists, if not, run roads.sql to create it
        try:
            conn = psycopg2.connect(
                host=os.getenv('PGHOST', 'localhost'),
                port=os.getenv('PGPORT', '5432'),
                user=os.getenv('PGUSER', 'postgres'),
                password=os.getenv('PGPASSWORD', ''),
                dbname=os.getenv('PGDATABASE', 'osm')
            )
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass('roads');")
                exists = cur.fetchone()[0]
                if not exists:
                    print("[GraphBuilder] 'roads' table not found. Running roads.sql...")
                    with open('scripts/roads.sql', 'r') as f:
                        sql = f.read()
                    cur.execute(sql)
                    conn.commit()
                    print("[GraphBuilder] 'roads' table created.")
                else:
                    cur.execute("SELECT COUNT(*) FROM roads;")
                    count = cur.fetchone()[0]
                    print(f"[GraphBuilder] Number of rows in roads table: {count}")
            conn.close()
        except Exception as e:
            print(f"[GraphBuilder] Failed to check or create roads table: {e}")

        # Try loading graph from cache
        if self._cache_path.exists():
            try:
                with self._cache_path.open('rb') as f:
                    cache = pickle.load(f)
                self.graph = cache.get('graph', {})
                self.node_index = cache.get('node_index', {})
                self.next_id = cache.get('next_id', len(self.node_index))
                return self.graph
            except Exception as e:
                print(f"[GraphBuilder] Failed to load cache: {e}")

        # Connect to database if cache is not available
        if not self._conn:
            self._conn = psycopg2.connect(
                host=os.getenv('PGHOST', 'localhost'),
                port=os.getenv('PGPORT', '5432'),
                user=os.getenv('PGUSER', 'postgres'),
                password=os.getenv('PGPASSWORD', ''),
                dbname=os.getenv('PGDATABASE', 'osm')
            )
        cur = self._conn.cursor()

        # Fetch road geometries from planet_osm_roads table
        cur.execute("SELECT id, ST_AsGeoJSON(geom) FROM roads;")
        rows = cur.fetchall()
        for road_id, geojson in rows:
            data = json.loads(geojson)
            if data.get('type') != 'LineString':
                continue
            coords: List[List[float]] = data.get('coordinates', [])
            if len(coords) < 2:
                continue
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

        # Persist cache
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            with self._cache_path.open('wb') as f:
                pickle.dump({
                    'graph': self.graph,
                    'node_index': self.node_index,
                    'next_id': self.next_id
                }, f)
        except Exception:
            pass
        return self.graph

    def close(self):
        if self._conn:
            self._conn.close()
