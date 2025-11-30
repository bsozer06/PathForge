# Copilot Instructions – Routing Engine MVP

This document defines instructions for Copilot to generate **simple, clear, and technologically consistent** code focused strictly on an MVP.

## 1. Project Goal

Build a simple routing engine that calculates the **shortest path** using OpenStreetMap (OSM) data.

## 2. Technology Stack

- **Backend:** Python 3.10+ + FastAPI  
- **GIS / Spatial Database:** PostGIS  
- **Routing Algorithm:** A* (MVP scope)  
- **Graph Handling:** In-memory Python graph structures  
- **Data Source:** OpenStreetMap (Geofabrik extracts)  
- **Frontend:** Angular + Leaflet (map rendering & interaction)

## 3. Coding Principles

- No unnecessary abstractions  
- Clean code with small, focused functions  
- Simple but consistent error handling  
- Open/Closed principle is **not required** — MVP speed and clarity first  
- Only **short and clear comments**

## 4. Project Folder Structure (MVP)

```
project/
  ├── backend/
  │   ├── api/
  │   │   └── routes.py
  │   ├── engine/
  │   │   ├── graph_builder.py
  │   │   ├── router.py
  │   │   └── heuristics.py
  │   ├── db/
  │   │   └── queries.py
  │   ├── main.py
  │   └── requirements.txt
  ├── frontend/
  │   ├── src/
  │   │   └── (Angular + Leaflet app)
  ├── scripts/
  │   └── load_osm.sh
```

## 5. Explicit Instructions for Copilot

- Implement **OSM → Graph** conversion in Python  
- Keep the graph structure simple:

```python
graph[node_id] = [{"to": neighbor_id, "cost": weight}]
```

- Implement the A* algorithm in a clear, step-by-step manner  
- Use **Haversine distance** as the heuristic  
- Fetch road geometries from PostGIS using `ST_AsGeoJSON(geom)`  
- Keep the graph fully in backend memory (no caching layer)  
- FastAPI endpoint definition:

```
POST /route
{
  "start": {"lat": 41.01, "lon": 28.97},
  "end":   {"lat": 41.08, "lon": 29.01}
}
```

- The response must be a **GeoJSON LineString**

## 6. Out of Scope (Do NOT Generate)

- Leaflet map rendering logic in the backend  
- Turn-by-turn navigation  
- Multiple routing profiles (car / bike / walk)  
- Advanced routing optimizations (CH, ALT, Contraction Hierarchies)  
- Microservices or event-driven architecture  
- Complex caching or distributed state

## 7. Example Tasks

- `graph_builder.py`: Fetch road segments from PostGIS → build Python graph  
- `router.py`: Implement A* routing algorithm  
- `heuristics.py`: Implement Haversine distance function  
- `routes.py`: FastAPI endpoint → call routing engine → return GeoJSON

---

These instructions guide Copilot to generate a **Python + FastAPI based, MVP-focused, clean, and production-oriented routing engine**.

