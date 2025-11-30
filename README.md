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

## PostGIS via Docker (Default Port 5434)
Start PostGIS directly with a single Docker command:
```powershell
docker run -d --name pg-postgis-5434 `
  -e POSTGRES_PASSWORD=StrongP@ssw0rd `
  -e POSTGRES_DB=osm `
  -p 5434:5432 `
  postgis/postgis:15-3.4
```
Enable extensions (inside the container):
```powershell
docker exec pg-postgis-5434 psql -U postgres -d osm -c "CREATE EXTENSION IF NOT EXISTS postgis;"
docker exec pg-postgis-5434 psql -U postgres -d osm -c "CREATE EXTENSION IF NOT EXISTS hstore;"
```
Update `.env` accordingly:
```
PGHOST=localhost
PGPORT=5434
PGUSER=postgres
PGPASSWORD=StrongP@ssw0rd
PGDATABASE=osm
```

Optional: use `scripts/setup_postgis.ps1` to run the same with defaults (port 5434) or override parameters.

## OSM Data Loading (Summary)
Use `scripts/load_osm.sh` as reference to import a regional extract with `osm2pgsql`, then create a `roads` table. Each road LineString feeds graph builder endpoints.

## Roadmap
1. Enrich graph with intermediate vertices & turn costs.
2. Add simple caching layer for graph (pickle / file snapshot).
3. Introduce input validation & structured error responses.
4. Add logging & metrics (timing, node counts).
5. Prepare for additional algorithms (Dijkstra, bidirectional A*).

README will be updated as capabilities expand.
