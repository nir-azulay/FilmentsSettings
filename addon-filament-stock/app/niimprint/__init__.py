"""Vendored niimprint BLE GATT library for Niimbot label printers.

Source: https://github.com/eigger/hass-niimbot
Supports B21 Pro (model 785, 300 DPI, 591px) via bleak.
"""

from .printer import PrinterClient, PrinterError
from .model import PrinterModel, get_printer_meta_by_model

__all__ = ["PrinterClient", "PrinterError", "PrinterModel", "get_printer_meta_by_model"]
