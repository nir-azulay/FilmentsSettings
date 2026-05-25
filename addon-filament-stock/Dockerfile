# syntax=docker/dockerfile:1.7
#
# Filament Stock Home Assistant add-on
#
# Stage 1: build the React/Vite frontend with Node.
# Stage 2: copy the built static bundle plus the FastAPI app into the HA
#          Alpine base image, install Python deps and nginx, and let s6-overlay
#          (provided by the HA base) supervise both services.

ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.22

# ---------- frontend build ----------
FROM node:22-alpine AS frontend

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build


# ---------- runtime ----------
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache \
        python3 \
        py3-pip \
        nginx \
    && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

COPY app/ /app/app/

# BambuStudio profile bundles -- served by the in-app downloader. Refresh
# from the canonical SUNLU/ and Inslogic/ folders with sync_profiles.sh.
COPY profiles/ /app/profiles/

COPY --from=frontend /build/dist/ /usr/share/nginx/html/

COPY rootfs/ /

RUN mkdir -p /config/data /var/log/nginx /var/lib/nginx/tmp

EXPOSE 8099

LABEL \
    io.hass.name="Filament Stock" \
    io.hass.description="3D printer filament inventory for Home Assistant" \
    io.hass.type="addon" \
    io.hass.version="0.1.0"
