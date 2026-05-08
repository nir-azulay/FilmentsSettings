# Filaments Stock Management

A web dashboard for managing 3D printer filament inventory. Tracks stock levels, purchase history, and provides low-stock alerts.

## Features

- Visual dashboard with color swatches for each filament
- Stock management (add purchases, track usage)
- Purchase history log per filament
- Low-stock alerts with configurable thresholds
- Import filament data from BambuStudio profile JSONs
- Color picker for each filament
- Amazon product links

## Quick Start (Docker)

```bash
cd stock-manager
docker compose up --build
```

Open http://localhost:3000 in your browser.

On first run, click **"Import from Profiles"** to auto-populate filaments from the existing profile JSONs.

## Architecture

- **Frontend**: React + Vite (served by nginx on port 80)
- **Backend**: Python FastAPI with SQLAlchemy (port 8000 internal)
- **Database**: SQLite (persisted via Docker volume)
- **Reverse Proxy**: nginx in the frontend container handles `/api/` -> backend

## Development (without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
PROFILES_ROOT="../.." uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/filaments | List all filaments with stock |
| POST | /api/filaments | Create filament |
| PUT | /api/filaments/:id | Update filament |
| DELETE | /api/filaments/:id | Delete filament |
| GET | /api/filaments/:id/history | Stock history |
| POST | /api/stock/:id | Add stock event |
| POST | /api/import | Import from profiles |
| GET | /api/alerts | Low-stock alerts |
| GET | /api/health | Health check |
