"""
SCD Backend — FastAPI Application Entry Point.

Start with:
    cd scd-system/backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import db
from app.models import create_tables
from app.routers import auth, conscrits, infractions, classement
from app.routers import websocket as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: connect to DB and create tables.
    Shutdown: close DB connection.
    """
    db.connect(reuse_if_open=True)
    create_tables()
    yield
    if not db.is_closed():
        db.close()


app = FastAPI(
    title="SCD — Système de Cohésion et Discipline",
    description=(
        "API backend pour le système de gestion de points, zones, "
        "infractions, et classements de la promotion."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(conscrits.router)
app.include_router(infractions.router)
app.include_router(classement.router)
app.include_router(ws_router.router)


# ── Health check ──────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "app": "SCD — Système de Cohésion et Discipline",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "database": "connected" if not db.is_closed() else "disconnected"}
