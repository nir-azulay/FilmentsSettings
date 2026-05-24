import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# When running as a Home Assistant add-on, /data is the persistent path managed
# by Supervisor and included in HA snapshots. Allow override via env for local
# development (e.g. running uvicorn from the repo without Docker).
DATA_DIR = os.environ.get("FILAMENT_STOCK_DATA_DIR", "/data")
DATABASE_URL = os.environ.get(
    "FILAMENT_STOCK_DATABASE_URL",
    f"sqlite:///{DATA_DIR}/filaments.db",
)

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
