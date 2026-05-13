from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ColorStockBase(BaseModel):
    color_name: str
    color_hex: str = "#808080"
    quantity: int = 0
    quantity_used: int = 0
    status: str = "in_stock"  # in_stock | ordered | out_of_stock
    order_id: Optional[str] = None


class ColorStockCreate(ColorStockBase):
    pass


class ColorStockUpdate(BaseModel):
    color_name: Optional[str] = None
    color_hex: Optional[str] = None
    quantity: Optional[int] = None
    quantity_used: Optional[int] = None
    status: Optional[str] = None
    order_id: Optional[str] = None


class ColorStockResponse(ColorStockBase):
    id: int
    filament_id: int
    quantity_used: int = 0
    order_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FilamentBase(BaseModel):
    brand: str
    material: str
    filament_type: str
    filament_id: Optional[str] = None
    density: Optional[float] = None
    nozzle_temp_min: Optional[int] = None
    nozzle_temp_max: Optional[int] = None
    bed_temp: Optional[int] = None
    amazon_url: str = ""
    brand_logo_url: str = ""
    notes: str = ""
    low_stock_threshold: int = 1


class FilamentCreate(FilamentBase):
    pass


class FilamentUpdate(BaseModel):
    brand: Optional[str] = None
    material: Optional[str] = None
    filament_type: Optional[str] = None
    filament_id: Optional[str] = None
    density: Optional[float] = None
    nozzle_temp_min: Optional[int] = None
    nozzle_temp_max: Optional[int] = None
    bed_temp: Optional[int] = None
    amazon_url: Optional[str] = None
    brand_logo_url: Optional[str] = None
    notes: Optional[str] = None
    low_stock_threshold: Optional[int] = None


class FilamentResponse(FilamentBase):
    id: int
    current_stock: int
    colors: list[ColorStockResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class StockEntryBase(BaseModel):
    quantity: int
    event_type: str
    color_stock_id: Optional[int] = None
    notes: str = ""


class StockEntryCreate(StockEntryBase):
    pass


class StockEntryResponse(StockEntryBase):
    id: int
    filament_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    filament_id: int
    brand: str
    material: str
    current_stock: int
    threshold: int
