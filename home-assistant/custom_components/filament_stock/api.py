"""Thin async wrapper around the Filament Stock add-on REST API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class FilamentStockApiError(Exception):
    """Raised when the add-on returns a non-success response or is unreachable."""


class FilamentStockApi:
    """Wraps the small surface of /api endpoints we use."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self._session = session
        self._base = base_url.rstrip("/")

    async def health(self) -> dict[str, Any]:
        return await self._get_json("/api/health")

    async def list_filaments(self) -> list[dict[str, Any]]:
        return await self._get_json("/api/filaments")

    async def list_alerts(self) -> list[dict[str, Any]]:
        return await self._get_json("/api/alerts")

    async def update_color(self, color_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request_json("PUT", f"/api/colors/{color_id}", json=payload)

    async def add_color(self, filament_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request_json(
            "POST", f"/api/filaments/{filament_id}/colors", json=payload
        )

    async def _get_json(self, path: str) -> Any:
        return await self._request_json("GET", path)

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self._base}{path}"
        try:
            async with asyncio.timeout(15):
                async with self._session.request(method, url, json=json) as resp:
                    if resp.status >= 400:
                        body = await resp.text()
                        raise FilamentStockApiError(
                            f"{method} {url} -> HTTP {resp.status}: {body[:200]}"
                        )
                    if resp.status == 204 or resp.content_length == 0:
                        return None
                    return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise FilamentStockApiError(f"{method} {url} failed: {err}") from err
