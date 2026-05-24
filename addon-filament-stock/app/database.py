import os
import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# When running as a Home Assistant add-on, /config is the user-visible
# persistent path mapped to \\homeassistant\addon_configs\filament_stock\
# via Samba and included in HA snapshots. Allow override via env for local
# development (e.g. running uvicorn from the repo without Docker).
DATA_DIR = os.environ.get("FILAMENT_STOCK_DATA_DIR", "/config/data")
DATABASE_URL = os.environ.get(
    "FILAMENT_STOCK_DATABASE_URL",
    f"sqlite:///{DATA_DIR}/filaments.db",
)


def _migrate_legacy_db() -> None:
    """If a v0.1.0 install left a DB at /data/filaments.db, copy it to /config/data
    once so the user-visible Samba path becomes authoritative."""
    legacy_path = "/data/filaments.db"
    new_path = os.path.join(DATA_DIR, "filaments.db")
    if (
        DATA_DIR == "/config/data"
        and os.path.exists(legacy_path)
        and not os.path.exists(new_path)
    ):
        os.makedirs(DATA_DIR, exist_ok=True)
        shutil.copy2(legacy_path, new_path)
        # Leave the legacy file in place as a backup; harmless and tiny.


_migrate_legacy_db()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
