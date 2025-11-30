# PathForge

Routing Engine MVP – Python + FastAPI.

## Goal
Calculate shortest path between two geographic points using OpenStreetMap (OSM) data loaded into PostGIS. Current algorithm: A* with Haversine heuristic.

## Backend Stack
- Python 3.10+
- FastAPI (HTTP API)
- PostGIS (road geometries)
- A* algorithm (in-memory graph)

## Folder Structure (MVP)
```
backend/
  main.py              FastAPI app bootstrap
  requirements.txt     Python dependencies
  api/routes.py        /route endpoint
  engine/heuristics.py Haversine distance
  engine/graph_builder.py OSM→Graph builder
  engine/router.py     A* implementation
  db/queries.py        DB connection helper
scripts/
  load_osm.sh          OSM import placeholder
```

## Graph Representation
```python
graph[node_id] = [{"to": neighbor_id, "cost": weight}]
```
Nodes represent road segment endpoints (MVP simplification).

## Route Endpoint
`POST /route`
Request body:
```json
{
  "start": {"lat": 41.01, "lon": 28.97},
  "end":   {"lat": 41.08, "lon": 29.01}
}
```
Response: GeoJSON Feature with LineString geometry of path.

## Environment Variables (.env)
```
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=yourpassword
PGDATABASE=osm
```

## Setup
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

## OSM Data Loading (Summary)
Use `scripts/load_osm.sh` as reference to import a regional extract with `osm2pgsql`, then create a `roads` table. Each road LineString feeds graph builder endpoints.

## Roadmap
1. Enrich graph with intermediate vertices & turn costs.
2. Add simple caching layer for graph (pickle / file snapshot).
3. Introduce input validation & structured error responses.
4. Add logging & metrics (timing, node counts).
5. Prepare for additional algorithms (Dijkstra, bidirectional A*).

README will be updated as capabilities expand.
