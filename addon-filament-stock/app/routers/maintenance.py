from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..color_merge import merge_duplicate_colors
from ..database import get_db

router = APIRouter(tags=["maintenance"])


@router.post("/maintenance/merge-duplicate-colors")
def merge_colors(db: Session = Depends(get_db)):
    return merge_duplicate_colors(db)
