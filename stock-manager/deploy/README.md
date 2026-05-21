# Filament Stock Manager - QNAP Docker Deployment

## Quick Start

1. Copy this entire `deploy` folder to your QNAP NAS (e.g. via SMB to `/share/Container/filament-stock/`)

2. SSH into your QNAP and navigate to the folder:
   ```bash
   cd /share/Container/filament-stock
   ```

3. Build and start:
   ```bash
   docker compose up -d --build
   ```

4. Open in browser:
   - **HTTP (LAN):** `http://<QNAP-IP>:3000` or `http://<QNAP-IP>:3080`
   - **HTTPS:** `https://<QNAP-IP>:3443` (self-signed certificate)

   If the browser still jumps to HTTPS on port 3000, use **:3080** or clear cached redirects / HSTS for the NAS IP (Chrome: `chrome://net-internals/#hsts` → Delete domain `192.168.10.11`).

5. Click **Import Profiles** in the UI to load all filament data.

## Architecture

- **Frontend** (port 3000): React + Vite, served by nginx. Proxies `/api/` to backend.
- **Backend** (internal port 8000): FastAPI + SQLite. Profile data is baked into the image.
- **Database**: SQLite stored in a Docker named volume (`db-data`) so it persists across container restarts and rebuilds.

## Updating Profiles

When you add new filament profiles to the main repo, re-run the generator script on your PC to rebuild the deploy folder, then copy it to QNAP and rebuild:

```bash
docker compose up -d --build
```

The database keeps your stock/color data in the `db-data` volume — rebuilding the images won't lose it.

## Changing the Port

Edit `docker-compose.yml` and change `"3000:80"` to your preferred port, e.g. `"8080:80"`.

## Stopping

```bash
docker compose down
```

To also remove the database volume (wipes all stock data):

```bash
docker compose down -v
```
