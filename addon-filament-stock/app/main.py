import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .addon_options import get_options, options_as_dict
from .database import Base, engine, DATA_DIR, DATABASE_URL
from .db_schema import apply_sqlite_migrations
from .health import build_health_report
from .profile_sync import sync_filaments_from_profiles
from .routers import alert_ignores, ams, analytics, assignments, filaments, maintenance, profiles, sharing, spools, stock
from .seed import seed_filaments, seed_filaments_force

_log = logging.getLogger("filament_stock")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

os.makedirs(DATA_DIR, exist_ok=True)
Base.metadata.create_all(bind=engine)
apply_sqlite_migrations()
seed_filaments()
sync_filaments_from_profiles()

# Pre-load add-on options so the log line lands at startup (and so any
# malformed /data/options.json is reported alongside the other init noise).
get_options()

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
app.include_router(spools.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(sharing.router, prefix="/api")


@app.get("/api/ping")
def ping():
    """Cheap liveness probe used by Docker / nginx / load balancers.

    Returns immediately without touching the DB or HA. For a full setup
    audit (HA reachable, ha-bambulab installed, AMS detected, etc.) use
    /api/health instead.
    """
    return {"status": "ok"}


@app.get("/api/health")
async def health_check():
    """Doctor / setup-checklist report.

    The frontend renders the failing checks as a sticky setup-card so a
    fresh install on someone else's HA system gets a guided walk-through
    instead of a silent blank screen. Heavier than /api/ping (talks to
    HA Core, enumerates services, opens the DB) but still cheap enough
    to call on every page load.
    """
    return await build_health_report()


@app.post("/api/seed-now")
def seed_now_endpoint():
    """Seed the sample filament list on demand.

    Used by the empty-state UI's "Or try our sample list" button so the
    user can populate the DB without having to flip the
    `seed_demo_filaments_on_first_run` option and restart the add-on.
    Idempotent -- existing rows are never overwritten.
    """
    summary = seed_filaments_force()
    return {"ok": True, **summary}


@app.get("/api/config")
def get_addon_config():
    """Return the user's resolved add-on options.

    The frontend reads this once on load to honour the preferences set in
    the HA Configuration tab (e.g. whether to ask about the replaced
    spool when assigning).
    """
    return options_as_dict()
