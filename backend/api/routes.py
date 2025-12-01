from fastapi import APIRouter, HTTPException
from fastapi import Request
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

@router.get('/status')
def status(request: Request):
    logging.info(f"[API] /status called from {request.client.host}")
    builder = engine_objects.get('builder')
    router_obj = engine_objects.get('router')
    initialized = bool(builder and router_obj and router_obj.graph)
    node_count = len(getattr(builder, 'node_index', {})) if builder else 0
    edge_count = sum(len(v) for v in getattr(router_obj, 'graph', {}).values()) if router_obj else 0
    resp = {
        "initialized": initialized,
        "nodes": node_count,
        "edges": edge_count
    }
    logging.info(f"[API] /status response: {resp}")
    return resp

@router.post('/route')
def route(req: RouteRequest, request: Request):
    logging.info(f"[API] /route called from {request.client.host} with: {req}")
    builder = engine_objects.get('builder')
    router_obj = engine_objects.get('router')
    if not builder or not router_obj:
        logging.error("[API] Routing engine not initialized")
        raise HTTPException(status_code=500, detail='Routing engine not initialized')
    coords = router_obj.route(req.start.lat, req.start.lon, req.end.lat, req.end.lon)
    if not coords:
        logging.warning(f"[API] Route not found for: {req}")
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
    logging.info(f"[API] /route response: {geojson}")
    return geojson
