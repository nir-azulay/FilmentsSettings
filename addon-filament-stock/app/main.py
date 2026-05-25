import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import Base, engine, DATA_DIR, DATABASE_URL
from .db_schema import apply_sqlite_migrations
from .routers import alert_ignores, ams, assignments, filaments, maintenance, profiles, stock
from .seed import seed_filaments

_log = logging.getLogger("filament_stock")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

os.makedirs(DATA_DIR, exist_ok=True)
Base.metadata.create_all(bind=engine)
apply_sqlite_migrations()
seed_filaments()

# Startup diagnostic so we always see which DB file the API is actually using
# and how many rows it has -- saves a lot of "why is it empty?" debugging.
try:
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else "missing"
    with engine.connect() as conn:
        f_count = conn.execute(text("SELECT COUNT(*) FROM filaments")).scalar()
        c_count = conn.execute(text("SELECT COUNT(*) FROM color_stocks")).scalar()
    _log.info(
        "DB ready: DATABASE_URL=%s file_size=%s filaments=%s color_stocks=%s",
        DATABASE_URL, db_size, f_count, c_count,
    )
except Exception as exc:  # pragma: no cover -- diagnostic only
    _log.warning("DB diagnostic failed: %r", exc)

app = FastAPI(title="Filaments Stock Management", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filaments.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(maintenance.router, prefix="/api")
app.include_router(alert_ignores.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(ams.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
