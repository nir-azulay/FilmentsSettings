"""BambuStudio profile bundle endpoints.

These expose the deployment-ready BambuStudio profiles bundled into the
add-on image, keyed by filament (matched on `<brand> <material>`).

  GET /filaments/{id}/profile           -> metadata + summary fields
  GET /filaments/{id}/profile/file/{n}  -> stream one bundled file
  GET /filaments/{id}/profile/zip       -> stream all bundled files as a zip
"""

from __future__ import annotations

import io
import zipfile
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Filament
from ..profile_bundle import ProfileBundle, bundle_for, file_path

router = APIRouter(tags=["profiles"])


def _load_bundle(filament_id: int, db: Session) -> tuple[Filament, ProfileBundle]:
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    bundle = bundle_for(filament.brand, filament.material)
    if not bundle:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No BambuStudio profile bundled for '{filament.brand} {filament.material}'."
                " See .cursor/rules/add-filament.mdc for how to author one."
            ),
        )
    return filament, bundle


@router.get("/filaments/{filament_id}/profile")
def get_profile_metadata(filament_id: int, db: Session = Depends(get_db)):
    """Return what's bundled for this filament + key fields pulled out of the
    base profile so the UI can render a summary without parsing the JSON
    itself."""
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    bundle = bundle_for(filament.brand, filament.material)
    if not bundle:
        return {
            "available": False,
            "product": f"{filament.brand} {filament.material}".strip(),
            "files": [],
            "nozzles": [],
            "summary": {},
        }
    return {
        "available": True,
        "product": bundle.product,
        "files": bundle.files,
        "base_file": bundle.base_file,
        "base_info": bundle.base_info,
        "preset_file": bundle.preset_file,
        "preset_info": bundle.preset_info,
        "nozzles": [
            {
                "nozzle_mm": n.nozzle_mm,
                "layer_height_mm": n.layer_height_mm,
                "file_name": n.file_name,
                "info_file": n.info_file,
            }
            for n in bundle.nozzles
        ],
        "summary": bundle.summary,
    }


@router.get("/filaments/{filament_id}/profile/file/{name:path}")
def download_profile_file(filament_id: int, name: str, db: Session = Depends(get_db)):
    filament, _ = _load_bundle(filament_id, db)
    path = file_path(filament.brand, filament.material, name)
    if not path:
        raise HTTPException(status_code=404, detail="File not in this filament's bundle")
    # JSON for .json, plain text for .info. Both are small so we let FastAPI
    # send them with FileResponse so byte-range, etag, etc. work for free.
    media = "application/json" if name.endswith(".json") else "text/plain; charset=utf-8"
    return FileResponse(
        path,
        media_type=media,
        filename=name,
        headers={
            # quote() handles spaces/parens in BambuStudio file names safely.
            "Content-Disposition": f'attachment; filename="{quote(name)}"',
        },
    )


@router.get("/filaments/{filament_id}/profile/zip")
def download_profile_zip(filament_id: int, db: Session = Depends(get_db)):
    filament, bundle = _load_bundle(filament_id, db)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in bundle.files:
            path = file_path(filament.brand, filament.material, name)
            if not path or not path.is_file():
                continue
            zf.write(path, arcname=name)
    buf.seek(0)
    # BambuStudio's import dialog accepts a folder; the README in the zip
    # tells the user where to drop the files.
    zip_name = f"{bundle.product} - BambuStudio profile.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{quote(zip_name)}"',
        },
    )
