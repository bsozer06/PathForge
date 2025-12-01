import os
from fastapi import FastAPI
from dotenv import load_dotenv
from .api.routes import router as api_router, engine_objects
from .engine.graph_builder import GraphBuilder
from .engine.router import Router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI(title="PathForge Routing Engine")

from contextlib import asynccontextmanager
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        builder = GraphBuilder()
        graph = builder.build()
        router = Router(graph, builder.node_index)
        engine_objects['builder'] = builder
        engine_objects['router'] = router
        logging.info(f"Routing engine initialized: nodes={len(builder.node_index)} edges={sum(len(v) for v in graph.values())}")
    except Exception as e:
        logging.error(f"Failed to initialize routing engine: {e}")
        # Fallback to empty graph; API will return 500/404 appropriately
        engine_objects['builder'] = None
        engine_objects['router'] = Router({}, {})
    yield
    builder = engine_objects.get('builder')
    if builder:
        builder.close()

app = FastAPI(title="PathForge Routing Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# For local run: uvicorn backend.main:app --reload
