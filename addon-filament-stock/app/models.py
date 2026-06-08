from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
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
    bed_temp_max = Column(Integer, nullable=True)
    chamber_temp = Column(Integer, nullable=True)
    dry_temp = Column(Integer, nullable=True)   # drying temperature in °C
    dry_time = Column(Integer, nullable=True)   # drying duration in hours
    amazon_url = Column(String, default="")
    brand_logo_url = Column(String, default="")
    notes = Column(String, default="")
    low_stock_threshold = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    colors = relationship("ColorStock", back_populates="filament", cascade="all, delete-orphan")
    stock_entries = relationship("StockEntry", back_populates="filament", cascade="all, delete-orphan")

    @property
    def current_stock(self) -> int:
        """Total available units across in_stock colors (spool + refill combined)."""
        total = 0
        for c in self.colors:
            status = c.status or "in_stock"
            if status != "in_stock":
                continue
            total += c.available_total
        return total


class ColorStock(Base):
    __tablename__ = "color_stocks"

    id = Column(Integer, primary_key=True, index=True)
    filament_id = Column(Integer, ForeignKey("filaments.id"), nullable=False)
    color_name = Column(String, nullable=False)
    color_hex = Column(String, default="#808080")
    # Spool counters (the original quantity/quantity_used columns -- kept as
    # the spool counters so existing integrations and history keep working).
    quantity = Column(Integer, default=0, nullable=False)
    quantity_used = Column(Integer, default=0, nullable=False)
    # Refill counters added in add-on 0.3.0. Refill = the inner cardboard core
    # of a Bambu-style refill pack, no plastic spool around it.
    quantity_refill = Column(Integer, default=0, nullable=False)
    used_refill = Column(Integer, default=0, nullable=False)
    status = Column(String, default="in_stock")  # in_stock | ordered | out_of_stock
    order_id = Column(String, nullable=True)  # e.g. Amazon order number
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    filament = relationship("Filament", back_populates="colors")

    @property
    def available_spool(self) -> int:
        return max(0, (self.quantity or 0) - (self.quantity_used or 0))

    @property
    def available_refill(self) -> int:
        return max(0, (self.quantity_refill or 0) - (self.used_refill or 0))

    @property
    def available_total(self) -> int:
        return self.available_spool + self.available_refill


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


class StapleAlertIgnore(Base):
    """User-dismissed low-stock staple (material type + black/white), all brands."""

    __tablename__ = "staple_alert_ignores"
    __table_args__ = (UniqueConstraint("filament_type", "color_key", name="uq_staple_ignore"),)

    id = Column(Integer, primary_key=True, index=True)
    filament_type = Column(String, nullable=False)  # PLA, PETG, ASA
    color_key = Column(String, nullable=False)  # black, white (normalized)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TrayAssignment(Base):
    """User-declared mapping from a Bambu AMS tray (or external spool) to a
    specific ColorStock row in our local DB.

    Added in add-on 0.6.0 for the "I just loaded this spool" workflow.

    Lifecycle:
      * On assign: a new row is inserted with `unassigned_at=NULL`. Any prior
        live row for the same `entity_id` is closed (its `unassigned_at` set
        to now) and its counter is incremented back.
      * On unassign: `unassigned_at` is set, the counter is incremented back.

    The history of past assignments is kept for the timeline view.

    `pushed_to_printer` records whether we also fired the
    `bambu_lab.set_filament` service when this assignment was made -- purely
    informational; the local stock decrement happens either way.
    """

    __tablename__ = "tray_assignments"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String, nullable=False, index=True)
    # Free-text label so the history view stays readable even after the AMS
    # unit numbering changes (e.g. a user adds a second AMS HT and the old
    # one's display index shifts from #1 to #2).
    location_label = Column(String, default="", nullable=False)
    color_stock_id = Column(Integer, ForeignKey("color_stocks.id"), nullable=False)
    # "spool" | "refill" -- which counter we decremented.
    packaging = Column(String, nullable=False)
    pushed_to_printer = Column(Integer, default=0, nullable=False)  # 0/1
    push_error = Column(String, default="", nullable=False)  # last push error, if any
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    unassigned_at = Column(DateTime, nullable=True, index=True)
    notes = Column(String, default="", nullable=False)

    color_stock = relationship("ColorStock")
    spool_instance = relationship("SpoolInstance", back_populates="tray_assignment", uselist=False)


class SpoolInstance(Base):
    """Individual physical spool or refill tracked with a unique scannable ID.

    Added in add-on 0.15.0. Each record represents one physical unit of
    filament (a spool or a refill cartridge) with a lifecycle:
    in_stock -> in_tray -> empty.
    """

    __tablename__ = "spool_instances"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, nullable=False, index=True)
    color_stock_id = Column(Integer, ForeignKey("color_stocks.id"), nullable=False)
    packaging = Column(String, nullable=False)  # spool | refill
    status = Column(String, default="in_stock", nullable=False)  # in_stock | in_tray | empty
    tray_entity_id = Column(String, nullable=True)
    tray_assignment_id = Column(Integer, ForeignKey("tray_assignments.id"), nullable=True)
    remain_pct = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    emptied_at = Column(DateTime, nullable=True)
    notes = Column(String, default="", nullable=False)

    color_stock = relationship("ColorStock")
    tray_assignment = relationship("TrayAssignment", back_populates="spool_instance")
    events = relationship("SpoolEvent", back_populates="spool_instance", cascade="all, delete-orphan", order_by="SpoolEvent.timestamp")


class SpoolEvent(Base):
    """Immutable log entry for a spool lifecycle transition.

    Kept forever so the timeline view shows the full history:
    created -> assigned (Tray 3) -> unassigned -> assigned (Tray 1) -> emptied.
    """

    __tablename__ = "spool_events"

    id = Column(Integer, primary_key=True, index=True)
    spool_id = Column(Integer, ForeignKey("spool_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # created | assigned | unassigned | emptied | deleted
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    details = Column(String, default="", nullable=False)  # JSON string with extra context

    spool_instance = relationship("SpoolInstance", back_populates="events")
