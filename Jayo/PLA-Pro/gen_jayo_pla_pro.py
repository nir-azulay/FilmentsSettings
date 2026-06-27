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
base.update({
    "filament_density": ["1.24"],
    "temperature_vitrification": ["65.3"],
    "filament_dev_ams_drying_heat_distortion_temperature": ["55"],
    "filament_dev_drying_softening_temperature": ["60"],
    "nozzle_temperature": ["220", "220"],
    "nozzle_temperature_initial_layer": ["220", "220"],
    "nozzle_temperature_range_low": ["195"],
    "nozzle_temperature_range_high": ["230"],
    "hot_plate_temp": ["60"],
    "hot_plate_temp_initial_layer": ["60"],
    "textured_plate_temp": ["60"],
    "textured_plate_temp_initial_layer": ["60"],
    "eng_plate_temp": ["0"],
    "eng_plate_temp_initial_layer": ["0"],
    "cool_plate_temp": ["35"],
    "cool_plate_temp_initial_layer": ["35"],
    "filament_flow_ratio": ["1.0", "1.0"],
    "filament_retraction_length": ["0.8", "0.8"],
    "filament_retraction_speed": ["35", "40"],
    "filament_deretraction_speed": ["35", "40"],
    "fan_max_speed": ["100"],
    "fan_min_speed": ["100"],
    "overhang_fan_speed": ["90"],
    "enable_pressure_advance": ["1"],
    "filament_dev_ams_drying_temperature": ["50", "50", "50", "50"],
    "filament_dev_ams_drying_time": ["4", "4", "4", "4"],
    "filament_dev_chamber_drying_time": ["4"],
    "filament_notes": (
        "Jayo PLA Pro Cold White. No manufacturer TDS is present in this repo; "
        "tuned as PLA Pro on Bambu H2S using the established PLA Pro baseline."
    ),
})

nozzles = ["0.2", "0.4", "0.6", "0.8"]
all_printers = [f"Bambu Lab H2S {nz} nozzle" for nz in nozzles]

filament_paths = []
for nz in nozzles:
    d = deepcopy(base)
    d["compatible_printers"] = all_printers
    d["name"] = f"Jayo PLA Pro Cold White @Bambu Lab H2S {nz} nozzle"
    d["filament_settings_id"] = [d["name"]]
    d["filament_max_volumetric_speed"] = ["2", "2"] if nz == "0.2" else ["12", "18"]

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
