from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..color_merge import normalize_color_name
from ..database import get_db
from ..low_stock import is_monitored_color_name, is_monitored_filament_type, staple_pool_key
from ..models import StapleAlertIgnore
from ..schemas import StapleAlertIgnoreCreate, StapleAlertIgnoreResponse

router = APIRouter(tags=["alert-ignores"])


@router.get("/alert-ignores", response_model=list[StapleAlertIgnoreResponse])
def list_alert_ignores(db: Session = Depends(get_db)):
    rows = db.query(StapleAlertIgnore).order_by(StapleAlertIgnore.filament_type, StapleAlertIgnore.color_key).all()
    return [
        StapleAlertIgnoreResponse(
            id=r.id,
            filament_type=r.filament_type,
            color_name=r.color_key.title(),
            color_key=r.color_key,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/alert-ignores", response_model=StapleAlertIgnoreResponse, status_code=201)
def create_alert_ignore(payload: StapleAlertIgnoreCreate, db: Session = Depends(get_db)):
    ft = payload.filament_type.strip().upper()
    if not is_monitored_filament_type(ft):
        raise HTTPException(status_code=400, detail="filament_type must be PLA, PETG, or ASA")
    if not is_monitored_color_name(payload.color_name):
        raise HTTPException(status_code=400, detail="color_name must be Black or White")

    color_key = normalize_color_name(payload.color_name)
    existing = (
        db.query(StapleAlertIgnore)
        .filter(StapleAlertIgnore.filament_type == ft, StapleAlertIgnore.color_key == color_key)
        .first()
    )
    if existing:
        return StapleAlertIgnoreResponse(
            id=existing.id,
            filament_type=existing.filament_type,
            color_name=existing.color_key.title(),
            color_key=existing.color_key,
            created_at=existing.created_at,
        )

    row = StapleAlertIgnore(filament_type=ft, color_key=color_key)
    db.add(row)
    db.commit()
    db.refresh(row)
    return StapleAlertIgnoreResponse(
        id=row.id,
        filament_type=row.filament_type,
        color_name=row.color_key.title(),
        color_key=row.color_key,
        created_at=row.created_at,
    )


@router.delete("/alert-ignores/{ignore_id}", status_code=204)
def delete_alert_ignore(ignore_id: int, db: Session = Depends(get_db)):
    row = db.query(StapleAlertIgnore).filter(StapleAlertIgnore.id == ignore_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Ignore rule not found")
    db.delete(row)
    db.commit()
