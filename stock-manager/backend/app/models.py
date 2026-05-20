from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Filament(Base):
    __tablename__ = "filaments"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    material = Column(String, nullable=False)
    filament_type = Column(String, nullable=False)
    filament_id = Column(String, unique=True, nullable=True)
    density = Column(Float, nullable=True)
    nozzle_temp_min = Column(Integer, nullable=True)
    nozzle_temp_max = Column(Integer, nullable=True)
    bed_temp = Column(Integer, nullable=True)
    amazon_url = Column(String, default="")
    brand_logo_url = Column(String, default="")
    notes = Column(String, default="")
    low_stock_threshold = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    colors = relationship("ColorStock", back_populates="filament", cascade="all, delete-orphan")
    stock_entries = relationship("StockEntry", back_populates="filament", cascade="all, delete-orphan")

    @property
    def current_stock(self) -> int:
        """Available spools (in_stock colors, quantity minus opened/used)."""
        total = 0
        for c in self.colors:
            status = c.status or "in_stock"
            if status != "in_stock":
                continue
            total += max(0, (c.quantity or 0) - (c.quantity_used or 0))
        return total


class ColorStock(Base):
    __tablename__ = "color_stocks"

    id = Column(Integer, primary_key=True, index=True)
    filament_id = Column(Integer, ForeignKey("filaments.id"), nullable=False)
    color_name = Column(String, nullable=False)
    color_hex = Column(String, default="#808080")
    quantity = Column(Integer, default=0)
    status = Column(String, default="in_stock")  # in_stock | ordered | out_of_stock
    order_id = Column(String, nullable=True)  # e.g. Amazon order number
    quantity_used = Column(Integer, default=0)  # spools consumed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    filament = relationship("Filament", back_populates="colors")


class StockEntry(Base):
    __tablename__ = "stock_entries"

    id = Column(Integer, primary_key=True, index=True)
    filament_id = Column(Integer, ForeignKey("filaments.id"), nullable=False)
    color_stock_id = Column(Integer, ForeignKey("color_stocks.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # "purchase", "used", "adjustment"
    notes = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    filament = relationship("Filament", back_populates="stock_entries")
    color_stock = relationship("ColorStock")
