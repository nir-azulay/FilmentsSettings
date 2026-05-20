import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import filaments, import_profiles, maintenance, stock

os.makedirs("data", exist_ok=True)
Base.metadata.create_all(bind=engine)

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
app.include_router(import_profiles.router, prefix="/api")
app.include_router(maintenance.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
