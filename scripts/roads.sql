-- Create roads table from osm2pgsql output (planet_osm_line)
-- Requires: osm2pgsql import done with --latlong into database 'osm'

CREATE TABLE IF NOT EXISTS roads AS
SELECT osm_id AS id, way AS geom
FROM planet_osm_line
WHERE highway IS NOT NULL;

CREATE INDEX IF NOT EXISTS roads_geom_idx ON roads USING GIST (geom);
ANALYZE roads;