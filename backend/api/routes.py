from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

class Point(BaseModel):
    lat: float
    lon: float

class RouteRequest(BaseModel):
    start: Point
    end: Point

router = APIRouter()

# Objects initialized externally and injected
engine_objects: Dict[str, Any] = {}

@router.post('/route')
def route(req: RouteRequest):
    builder = engine_objects.get('builder')
    router_obj = engine_objects.get('router')
    if not builder or not router_obj:
        raise HTTPException(status_code=500, detail='Routing engine not initialized')
    coords = router_obj.route(req.start.lat, req.start.lon, req.end.lat, req.end.lon)
    if not coords:
        raise HTTPException(status_code=404, detail='Route not found')
    # GeoJSON LineString
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[lon, lat] for (lat, lon) in coords]
        },
        "properties": {
            "points": len(coords)
        }
    }
    return geojson
