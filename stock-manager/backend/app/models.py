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
    color_name = Column(String, default="")
    color_hex = Column(String, default="#808080")
    density = Column(Float, nullable=True)
    nozzle_temp_min = Column(Integer, nullable=True)
    nozzle_temp_max = Column(Integer, nullable=True)
    bed_temp = Column(Integer, nullable=True)
    amazon_url = Column(String, default="")
    brand_logo_url = Column(String, default="")
    notes = Column(String, default="")
    low_stock_threshold = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    stock_entries = relationship("StockEntry", back_populates="filament", cascade="all, delete-orphan")

    @property
    def current_stock(self) -> int:
        return sum(e.quantity for e in self.stock_entries)


class StockEntry(Base):
    __tablename__ = "stock_entries"

    id = Column(Integer, primary_key=True, index=True)
    filament_id = Column(Integer, ForeignKey("filaments.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # "purchase", "used", "adjustment"
    notes = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    filament = relationship("Filament", back_populates="stock_entries")
