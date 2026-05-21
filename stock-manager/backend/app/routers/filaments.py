from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..color_merge import find_color_by_name
from ..low_stock import build_staple_pools, iter_low_stock_colors, load_ignored_staple_keys
from ..models import StapleAlertIgnore
from ..database import get_db
from ..models import ColorStock, Filament
from ..schemas import (
    AlertResponse,
    ColorStockCreate,
    ColorStockResponse,
    ColorStockUpdate,
    FilamentCreate,
    FilamentResponse,
    FilamentUpdate,
)

router = APIRouter(tags=["filaments"])


@router.get("/filaments", response_model=list[FilamentResponse])
def list_filaments(db: Session = Depends(get_db)):
    filaments = db.query(Filament).order_by(Filament.brand, Filament.material).all()
    return [_to_response(f) for f in filaments]


@router.post("/filaments", response_model=FilamentResponse, status_code=201)
def create_filament(payload: FilamentCreate, db: Session = Depends(get_db)):
    filament = Filament(**payload.model_dump())
    db.add(filament)
    db.commit()
    db.refresh(filament)
    return _to_response(filament)


@router.get("/filaments/{filament_id}", response_model=FilamentResponse)
def get_filament(filament_id: int, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    return _to_response(filament)


@router.put("/filaments/{filament_id}", response_model=FilamentResponse)
def update_filament(filament_id: int, payload: FilamentUpdate, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(filament, key, value)
    db.commit()
    db.refresh(filament)
    return _to_response(filament)


@router.delete("/filaments/{filament_id}", status_code=204)
def delete_filament(filament_id: int, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    db.delete(filament)
    db.commit()


# --- Color stock endpoints ---

@router.post("/filaments/{filament_id}/colors", response_model=ColorStockResponse, status_code=201)
def add_color(filament_id: int, payload: ColorStockCreate, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")

    existing = find_color_by_name(db, filament_id, payload.color_name)
    if existing:
        data = payload.model_dump()
        add_qty = data.get("quantity") or 0
        existing.quantity = (existing.quantity or 0) + add_qty
        if data.get("color_hex"):
            existing.color_hex = data["color_hex"]
        if existing.status != "in_stock" and data.get("status") == "in_stock":
            existing.status = "in_stock"
        db.commit()
        db.refresh(existing)
        return existing

    data = payload.model_dump()
    data["color_name"] = " ".join(payload.color_name.strip().split())
    color = ColorStock(filament_id=filament_id, **data)
    db.add(color)
    db.commit()
    db.refresh(color)
    return color


@router.put("/colors/{color_id}", response_model=ColorStockResponse)
def update_color(color_id: int, payload: ColorStockUpdate, db: Session = Depends(get_db)):
    color = db.query(ColorStock).filter(ColorStock.id == color_id).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(color, key, value)
    db.commit()
    db.refresh(color)
    return color


@router.delete("/colors/{color_id}", status_code=204)
def delete_color(color_id: int, db: Session = Depends(get_db)):
    color = db.query(ColorStock).filter(ColorStock.id == color_id).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color not found")
    db.delete(color)
    db.commit()


# --- Alerts ---

@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    filaments = db.query(Filament).all()
    pools = build_staple_pools(filaments)
    ignored = load_ignored_staple_keys(db.query(StapleAlertIgnore).all())
    alerts = []
    for f in filaments:
        for color, avail, threshold in iter_low_stock_colors(f, pools, ignored):
            alerts.append(AlertResponse(
                filament_id=f.id,
                color_stock_id=color.id,
                brand=f.brand,
                material=f.material,
                filament_type=f.filament_type,
                color_name=color.color_name,
                current_stock=avail,
                threshold=threshold,
            ))
    return alerts


def _to_response(filament: Filament) -> FilamentResponse:
    return FilamentResponse(
        id=filament.id,
        brand=filament.brand,
        material=filament.material,
        filament_type=filament.filament_type,
        filament_id=filament.filament_id,
        density=filament.density,
        nozzle_temp_min=filament.nozzle_temp_min,
        nozzle_temp_max=filament.nozzle_temp_max,
        bed_temp=filament.bed_temp,
        amazon_url=filament.amazon_url,
        brand_logo_url=filament.brand_logo_url,
        notes=filament.notes,
        low_stock_threshold=filament.low_stock_threshold,
        current_stock=filament.current_stock,
        colors=filament.colors,
        created_at=filament.created_at,
    )
