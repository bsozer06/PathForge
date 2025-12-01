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

## Automated Setup (scripts/import_osm.ps1)
Prefer a single command that handles network setup, PostGIS start, extension enablement, OSM import, `roads` creation, and verification.

Quick run (from repo root):
```powershell
.\scripts\import_osm.ps1 -PbfFile "C:\_burhan\_projects\PathForge\turkey-latest.osm.pbf"
```

Common options:
- `-HostPort 5434` change host port
- `-DbName osm` set database name
- `-SkipImport` skip the OSM import step
- `-SkipRoads` skip applying `scripts\roads.sql`
 - `-BBox "minlon,minlat,maxlon,maxlat"` import only this bounding box (PBF must cover this area)


### Import OSM with Bounding Box (Step-by-Step)

1. **Download OSM PBF file**
  - Example (Turkey):
    ```powershell
    Invoke-WebRequest -Uri https://download.geofabrik.de/europe/turkey-latest.osm.pbf -OutFile turkey-latest.osm.pbf
    ```

2. **Run the import script with a bounding box**
  - Replace the coordinates with your area of interest:
    ```powershell
    .\scripts\import_osm.ps1 -PbfFile "C:\_burhan\_projects\PathForge\turkey-latest.osm.pbf" -BBox "28.90,41.00,29.10,41.10"
    ```
  - `-BBox` format: `minlon,minlat,maxlon,maxlat` (e.g., Istanbul region)
  - The PBF file must cover the bounding box area you specify.

3. **What the script does**
  - Ensures Docker network and PostGIS container are running
  - Enables required extensions (`postgis`, `hstore`)
  - Imports only the data within your bounding box using `osm2pgsql`
  - Creates the `roads` table and spatial index
  - Prints the number of imported roads and recommended `.env` settings

4. **Verify import**
  - Check road count:
    ```powershell
    docker exec pg-postgis-5434 psql -U postgres -d osm -c "SELECT COUNT(*) FROM roads;"
    ```
  - Or run the Python DB check:
    ```powershell
    . .venv\Scripts\Activate.ps1
    python backend\tools\db_check.py
    ```

5. **Troubleshooting**
  - If you get a file not found error, check your path and filename.
  - If the bounding box is outside the PBF coverage, import will be empty.
  - For large areas, import may take a long time and use significant disk space.

6. **Example bounding boxes**
  - Istanbul: `28.90,41.00,29.10,41.10`
  - Ankara: `32.80,39.80,33.00,40.00`
  - Izmir: `26.90,38.30,27.30,38.60`

## OSM Import (Docker-based)
Download a Geofabrik extract (example: Turkey):
```powershell
Invoke-WebRequest -Uri https://download.geofabrik.de/europe/turkey-latest.osm.pbf -OutFile turkey-latest.osm.pbf
```

Preferred: use a shared Docker network and connect container-to-container.

Setup network and PostGIS:
```powershell
docker network create pathforge-net
docker run -d --name pg-postgis-5434 --network pathforge-net `
  -e POSTGRES_PASSWORD=StrongP@ssw0rd -e POSTGRES_DB=osm `
  -p 5434:5432 postgis/postgis:15-3.4

# Enable required extensions
docker exec pg-postgis-5434 psql -U postgres -d osm -c "CREATE EXTENSION IF NOT EXISTS postgis;"
docker exec pg-postgis-5434 psql -U postgres -d osm -c "CREATE EXTENSION IF NOT EXISTS hstore;"
```

Import OSM with `osm2pgsql` on the same network (directly to PostGIS):
```powershell
docker run --rm --network pathforge-net -v "C:\_burhan\_projects\PathForge:/data" `
  -e PGPASSWORD=StrongP@ssw0rd iboates/osm2pgsql:latest `
  osm2pgsql -d osm -U postgres --host pg-postgis-5434 --port 5432 `
  --create --slim --hstore --latlong /data/turkey-latest.osm.pbf
```

Create the `roads` table from `planet_osm_line`:
```powershell
# Option A: pipe SQL directly (no copy)
docker exec -i pg-postgis-5434 psql -U postgres -d osm < scripts\roads.sql

# Option B: create a folder and run from file
docker exec pg-postgis-5434 sh -c "mkdir -p /data"
docker cp scripts\roads.sql pg-postgis-5434:/data/roads.sql
docker exec pg-postgis-5434 psql -U postgres -d osm -f /data/roads.sql
```

Verify data:
```powershell
docker exec pg-postgis-5434 psql -U postgres -d osm -c "SELECT COUNT(*) FROM roads;"
. .venv\Scripts\Activate.ps1
python backend\tools\db_check.py
```

## Quick Backend Run
Start the FastAPI server once data is loaded and your `.env` is set:
```powershell
# From repo root
. .\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload
```

Test the route endpoint:
```powershell
$body = @{ start = @{ lat = 41.01; lon = 28.97 }; end = @{ lat = 41.08; lon = 29.01 } } | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/route -Method Post -ContentType "application/json" -Body $body
```

Notes:
- If you prefer host networking, you can import with `--host host.docker.internal --port 5434` but the shared network approach is more reliable.
- For smaller datasets, use a city-level extract or `osm2pgsql` with a bounding box.

## Roadmap
1. Enrich graph with intermediate vertices & turn costs.
2. Add simple caching layer for graph (pickle / file snapshot).
3. Introduce input validation & structured error responses.
4. Add logging & metrics (timing, node counts).
5. Prepare for additional algorithms (Dijkstra, bidirectional A*).

README will be updated as capabilities expand.
