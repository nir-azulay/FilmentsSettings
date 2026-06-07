from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, computed_field


# `PackagingType` is the new per-action discriminator used by stock services
# (use_spool, add_purchase, set_status) to say which counter to touch.
PackagingType = Literal["spool", "refill"]


class ColorStockBase(BaseModel):
    color_name: str
    color_hex: str = "#808080"
    # Spool counters (the original quantity / quantity_used columns).
    quantity: int = Field(default=0, ge=0)
    quantity_used: int = Field(default=0, ge=0)
    # Refill counters (added in add-on 0.3.0).
    quantity_refill: int = Field(default=0, ge=0)
    used_refill: int = Field(default=0, ge=0)
    status: str = "in_stock"  # in_stock | ordered | out_of_stock
    order_id: Optional[str] = None


class ColorStockCreate(ColorStockBase):
    pass


class ColorStockUpdate(BaseModel):
    color_name: Optional[str] = None
    color_hex: Optional[str] = None
    quantity: Optional[int] = None
    quantity_used: Optional[int] = None
    quantity_refill: Optional[int] = None
    used_refill: Optional[int] = None
    status: Optional[str] = None
    order_id: Optional[str] = None


class ColorStockResponse(ColorStockBase):
    id: int
    filament_id: int
    created_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def available_spool(self) -> int:
        return max(0, (self.quantity or 0) - (self.quantity_used or 0))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def available_refill(self) -> int:
        return max(0, (self.quantity_refill or 0) - (self.used_refill or 0))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def available_total(self) -> int:
        return self.available_spool + self.available_refill

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
    bed_temp_max: Optional[int] = None
    chamber_temp: Optional[int] = None
    amazon_url: str = ""
    brand_logo_url: str = ""
    notes: str = ""
    low_stock_threshold: int = 1


class FilamentCreate(FilamentBase):
    # Override to Optional so the router can tell "the client didn't specify
    # a threshold, fill in the user's configured default" apart from "the
    # client explicitly chose 1". model_dump(exclude_unset=True) gives us
    # the right signal.
    low_stock_threshold: Optional[int] = None


class FilamentUpdate(BaseModel):
    brand: Optional[str] = None
    material: Optional[str] = None
    filament_type: Optional[str] = None
    filament_id: Optional[str] = None
    density: Optional[float] = None
    nozzle_temp_min: Optional[int] = None
    nozzle_temp_max: Optional[int] = None
    bed_temp: Optional[int] = None
    bed_temp_max: Optional[int] = None
    chamber_temp: Optional[int] = None
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
    color_stock_id: int
    brand: str
    material: str
    filament_type: str
    color_name: str
    current_stock: int
    threshold: int


class StapleAlertIgnoreCreate(BaseModel):
    filament_type: str
    color_name: str


class StapleAlertIgnoreResponse(BaseModel):
    id: int
    filament_type: str
    color_name: str
    color_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── SpoolInstance (0.15.0) ──────────────────────────────────────────────────

SpoolStatus = Literal["in_stock", "in_tray", "empty"]


class SpoolInstanceCreate(BaseModel):
    color_stock_id: int
    packaging: PackagingType
    notes: str = ""


class SpoolInstanceUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    remain_pct: Optional[int] = None


class SpoolInstanceResponse(BaseModel):
    id: int
    uid: str
    color_stock_id: int
    packaging: str
    status: str
    tray_entity_id: Optional[str] = None
    tray_assignment_id: Optional[int] = None
    remain_pct: Optional[int] = None
    created_at: datetime
    assigned_at: Optional[datetime] = None
    emptied_at: Optional[datetime] = None
    notes: str = ""
    brand: Optional[str] = None
    material: Optional[str] = None
    filament_type: Optional[str] = None
    color_name: Optional[str] = None
    color_hex: Optional[str] = None
    nozzle_temp_min: Optional[int] = None
    nozzle_temp_max: Optional[int] = None
    bed_temp: Optional[int] = None
    bed_temp_max: Optional[int] = None
    chamber_temp: Optional[int] = None

    model_config = {"from_attributes": True}
