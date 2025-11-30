#!/usr/bin/env bash
# Placeholder script for loading OSM data into PostGIS.
# Steps (adjust region + file names):
# 1. Download extract: wget https://download.geofabrik.de/europe/turkey-latest.osm.pbf
# 2. Import with osm2pgsql (ensure installed):
#    osm2pgsql -d osm -U postgres --create --slim --hstore --latlong turkey-latest.osm.pbf
# 3. Create simplified roads table (example):
#    psql -d osm -c "CREATE TABLE roads AS SELECT osm_id AS id, way AS geom FROM planet_osm_line WHERE highway IS NOT NULL;"
# 4. Ensure spatial index: psql -d osm -c "CREATE INDEX roads_geom_idx ON roads USING GIST(geom);"
# 5. Vacuum analyze: psql -d osm -c "VACUUM ANALYZE roads;"

exit 0
