from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Filament
from ..schemas import (
    AlertResponse,
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


@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    filaments = db.query(Filament).all()
    alerts = []
    for f in filaments:
        stock = f.current_stock
        if stock <= f.low_stock_threshold:
            alerts.append(AlertResponse(
                filament_id=f.id,
                brand=f.brand,
                material=f.material,
                color_name=f.color_name,
                current_stock=stock,
                threshold=f.low_stock_threshold,
            ))
    return alerts


def _to_response(filament: Filament) -> FilamentResponse:
    return FilamentResponse(
        id=filament.id,
        brand=filament.brand,
        material=filament.material,
        filament_type=filament.filament_type,
        filament_id=filament.filament_id,
        color_name=filament.color_name,
        color_hex=filament.color_hex,
        density=filament.density,
        nozzle_temp_min=filament.nozzle_temp_min,
        nozzle_temp_max=filament.nozzle_temp_max,
        bed_temp=filament.bed_temp,
        amazon_url=filament.amazon_url,
        brand_logo_url=filament.brand_logo_url,
        notes=filament.notes,
        low_stock_threshold=filament.low_stock_threshold,
        current_stock=filament.current_stock,
        created_at=filament.created_at,
    )
