from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Filament, StockEntry
from ..schemas import StockEntryCreate, StockEntryResponse

router = APIRouter(tags=["stock"])


@router.get("/filaments/{filament_id}/history", response_model=list[StockEntryResponse])
def get_stock_history(filament_id: int, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    entries = (
        db.query(StockEntry)
        .filter(StockEntry.filament_id == filament_id)
        .order_by(StockEntry.created_at.desc())
        .all()
    )
    return entries


@router.post("/stock/{filament_id}", response_model=StockEntryResponse, status_code=201)
def add_stock_event(filament_id: int, payload: StockEntryCreate, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    if payload.event_type not in ("purchase", "used", "adjustment"):
        raise HTTPException(status_code=400, detail="event_type must be 'purchase', 'used', or 'adjustment'")
    entry = StockEntry(
        filament_id=filament_id,
        quantity=payload.quantity,
        event_type=payload.event_type,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
