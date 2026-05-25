#!/usr/bin/env python3
"""Generate Jayo PLA Pro Cold White profiles for Bambu Lab H2S."""

import json
import os
import time
import zipfile
from copy import deepcopy
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = Path(r"c:\GitHub\filments settings\Inslogic\Inslogic PLA Pro @Bambu Lab H2S.json")

with open(TEMPLATE) as f:
    base = json.load(f)

base["filament_vendor"] = ["Jayo"]
base["filament_id"] = "Pj1a2b3c4"
base["filament_notes"] = "Jayo PLA Pro Cold White. Based on Generic PLA settings."

nozzles = ["0.2", "0.4", "0.6", "0.8"]
all_printers = [f"Bambu Lab H2S {nz} nozzle" for nz in nozzles]

filament_paths = []
for nz in nozzles:
    d = deepcopy(base)
    d["compatible_printers"] = all_printers
    d["name"] = f"Jayo PLA Pro Cold White @Bambu Lab H2S {nz} nozzle"
    d["filament_settings_id"] = [d["name"]]

    fname = f"{d['name']}.json"
    out = SCRIPT_DIR / fname
    with open(out, "w", newline="\n") as f:
        json.dump(d, f, indent=4, sort_keys=True)
        f.write("\n")
    filament_paths.append(f"Jayo/{fname}")
    print(f"  Created: {fname}")

bundle = {
    "bundle_id": f"2189385007_Jayo PLA Pro Cold White_{int(time.time())}",
    "bundle_type": "filament config bundle",
    "filament_name": "Jayo PLA Pro Cold White",
    "filament_vendor": [{"filament_path": filament_paths, "vendor": "Jayo"}],
    "version": "02.06.01.50",
}
bs_path = SCRIPT_DIR / "bundle_structure.json"
with open(bs_path, "w", newline="\n") as f:
    json.dump(bundle, f, indent=4)
    f.write("\n")
print("  Created: bundle_structure.json")

bbsflmt = SCRIPT_DIR / "Jayo PLA Pro Cold White.bbsflmt"
with zipfile.ZipFile(bbsflmt, "w", zipfile.ZIP_DEFLATED) as zf:
    for nz in nozzles:
        fname = f"Jayo PLA Pro Cold White @Bambu Lab H2S {nz} nozzle.json"
        zf.write(SCRIPT_DIR / fname, f"Jayo/{fname}")
    zf.write(bs_path, "bundle_structure.json")
print(f"  Packed: {bbsflmt}")
