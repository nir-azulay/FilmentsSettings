"""Wrapper around the vendored niimprint BLE library for Niimbot B21 Pro.

Connects to the printer via Bluetooth LE (bleak), sends a PIL image,
and returns a result dict.
"""

from __future__ import annotations

import logging
from typing import Any

from PIL import Image

_log = logging.getLogger("filament_stock.niimbot")

# B21 Pro defaults
DEFAULT_DENSITY = 3
DEFAULT_WAIT_BETWEEN_LINES = 0.002
DEFAULT_BATCH_SIZE = 4


async def print_to_niimbot(
    image: Image.Image,
    printer_address: str,
    density: int = DEFAULT_DENSITY,
) -> dict[str, Any]:
    """Send a label image to a Niimbot B21 Pro over BLE.

    Returns {"ok": True, "duration": <seconds>} on success,
    or {"ok": False, "error": "<message>"} on failure.
    """
    try:
        from bleak import BleakClient, BleakScanner
        from bleak_retry_connector import establish_connection
        from .niimprint.printer import PrinterClient, InfoEnum
        from .niimprint.model import PrinterModel, get_printer_meta_by_id
    except ImportError as exc:
        return {"ok": False, "error": f"Missing BLE dependency: {exc}"}

    try:
        _log.info("Scanning for Niimbot at %s ...", printer_address)
        device = await BleakScanner.find_device_by_address(printer_address, timeout=10.0)
        if not device:
            return {"ok": False, "error": f"Printer {printer_address} not found via BLE scan"}

        _log.info("Connecting to %s (%s) ...", device.name, device.address)
        client = await establish_connection(BleakClient, device, device.address)
        if not client.is_connected:
            return {"ok": False, "error": "Failed to establish BLE connection"}

        try:
            printer = PrinterClient(client)
            await printer.start_notify()

            device_type = await printer.get_info(InfoEnum.DEVICETYPE)
            if device_type is not None:
                meta = get_printer_meta_by_id(int(device_type))
                model_name = meta["model"].name if meta else str(device_type)
                _log.info("Detected printer model: %s (id=%s)", model_name, device_type)
            else:
                model_name = PrinterModel.B21_PRO.name

            try:
                printer_model = PrinterModel(model_name)
            except (ValueError, TypeError):
                printer_model = PrinterModel.B21_PRO
                _log.warning("Unknown model %r, defaulting to B21_PRO", model_name)

            import time
            start = time.time()
            await printer.print_image(
                printer_model,
                image,
                density,
                DEFAULT_WAIT_BETWEEN_LINES,
                DEFAULT_BATCH_SIZE,
            )
            duration = time.time() - start
            await printer.stop_notify()
            _log.info("Print completed in %.1f seconds", duration)
            return {"ok": True, "duration": round(duration, 1)}
        finally:
            if client.is_connected:
                await client.disconnect()

    except Exception as exc:
        _log.exception("Niimbot print failed")
        return {"ok": False, "error": str(exc)}
