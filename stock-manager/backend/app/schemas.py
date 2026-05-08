from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FilamentBase(BaseModel):
    brand: str
    material: str
    filament_type: str
    filament_id: Optional[str] = None
    color_name: str = ""
    color_hex: str = "#808080"
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
    color_name: Optional[str] = None
    color_hex: Optional[str] = None
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
    created_at: datetime

    model_config = {"from_attributes": True}


class StockEntryBase(BaseModel):
    quantity: int
    event_type: str
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
    color_name: str
    current_stock: int
    threshold: int
