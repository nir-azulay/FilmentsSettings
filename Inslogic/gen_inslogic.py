#!/usr/bin/env python3
"""
Generate Inslogic filament profiles for Bambu Lab H2S.

Settings are identical to Bambu Lab system profiles for each material type —
giving a clean starting point to tune per-filament if needed later.

Produces profiles for:
  - Inslogic PETG Pro   (High-Speed Matte PETG)
  - Inslogic ASA        (UV & Weather resistant ASA)
  - Inslogic TPU 95A    (Flexible TPU — no 0.2mm nozzle)
  - Inslogic Matte PLA  (Fine matte texture PLA)
  - Inslogic PLA Pro    (Strong & Tough PLA Pro)
  - Inslogic Silk PLA   (Silky smooth PLA)
  - Inslogic Nebulux PLA (Special effect PLA)
"""

from __future__ import annotations

import json
import secrets
import shutil
import time
from copy import deepcopy
from pathlib import Path

VERSION   = "2.6.0.2"
USER_ID   = "2189385007"
TIMESTAMP = str(int(time.time()))

SCRIPT_DIR   = Path(__file__).resolve().parent
REPO_ROOT    = SCRIPT_DIR.parent
DEPLOY_DIR   = REPO_ROOT / "DeployPack"
TEMPLATE_PATH = SCRIPT_DIR / "baseline_full_filament.json"

ALL_H2S_NOZZLES = [
    "Bambu Lab H2S 0.2 nozzle",
    "Bambu Lab H2S 0.4 nozzle",
    "Bambu Lab H2S 0.6 nozzle",
    "Bambu Lab H2S 0.8 nozzle",
]

PROCESS_PARENT = {
    "0.2": ("0.10mm Standard @BBL H2S 0.2 nozzle", "GP152", "0.10"),
    "0.4": ("0.20mm Standard @BBL H2S",             "GP158", "0.20"),
    "0.6": ("0.30mm Standard @BBL H2S 0.6 nozzle",  "GP159", "0.30"),
    "0.8": ("0.40mm Standard @BBL H2S 0.8 nozzle",  "GP156", "0.40"),
}

# ─── Shared gcode (same as Bambu PETG/PLA system profiles) ────────────────────

PETG_START_GCODE = (
    "; filament start gcode\n"
    "{if (bed_temperature[current_extruder] >80)||(bed_temperature_initial_layer[current_extruder] >80)}"
    "M106 P3 S255\n"
    "{elsif (bed_temperature[current_extruder] >60)||(bed_temperature_initial_layer[current_extruder] >60)}"
    "M106 P3 S180\n"
    "{endif}\n\n"
    "{if activate_air_filtration[current_extruder] && support_air_filtration}\n"
    "M106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n"
    "{endif}"
)

ASA_START_GCODE = (
    "; filament start gcode\n"
    "{if (bed_temperature[current_extruder] >80)||(bed_temperature_initial_layer[current_extruder] >80)}"
    "M106 P3 S255\n"
    "{elsif (bed_temperature[current_extruder] >60)||(bed_temperature_initial_layer[current_extruder] >60)}"
    "M106 P3 S180\n"
    "{endif}\n\n"
    "{if activate_air_filtration[current_extruder] && support_air_filtration}\n"
    "M106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n"
    "{endif}"
)

# ─── Filament definitions — settings match Bambu system profiles exactly ──────

FILAMENTS = [
    {
        # Bambu reference: Generic PETG-HS / Bambu PETG Basic HF
        "short":         "Inslogic PETG Pro",
        "filament_id":   "Pi1a2b3c4",
        "filament_type": "PETG",
        "nozzles":       ["0.2", "0.4", "0.6", "0.8"],
        "settings": {
            "filament_density":                 ["1.27"],
            "temperature_vitrification":        ["65"],
            "nozzle_temperature":               ["245", "255"],
            "nozzle_temperature_initial_layer": ["250", "260"],
            "nozzle_temperature_range_low":     ["235"],
            "nozzle_temperature_range_high":    ["270"],
            "filament_max_volumetric_speed":    ["18", "28"],
            "filament_retraction_length":       ["1.0", "1.0"],
            "filament_retraction_speed":        ["35", "40"],
            "filament_deretraction_speed":      ["35", "40"],
            "fan_max_speed":                    ["60"],
            "fan_min_speed":                    ["20"],
            "overhang_fan_speed":               ["50"],
            "hot_plate_temp":                   ["70"],
            "hot_plate_temp_initial_layer":     ["70"],
            "textured_plate_temp":              ["70"],
            "textured_plate_temp_initial_layer":["70"],
            "eng_plate_temp":                   ["0"],
            "eng_plate_temp_initial_layer":     ["0"],
            "filament_start_gcode":             [PETG_START_GCODE],
        },
    },
    {
        # Bambu reference: Bambu ASA / Generic ASA on H2S
        "short":         "Inslogic ASA",
        "filament_id":   "Pi2b3c4d5",
        "filament_type": "ASA",
        "nozzles":       ["0.2", "0.4", "0.6", "0.8"],
        "settings": {
            "filament_density":                 ["1.07"],
            "temperature_vitrification":        ["98"],
            "nozzle_temperature":               ["270", "270"],
            "nozzle_temperature_initial_layer": ["270", "270"],
            "nozzle_temperature_range_low":     ["240"],
            "nozzle_temperature_range_high":    ["290"],
            "filament_max_volumetric_speed":    ["12", "20"],
            "filament_retraction_length":       ["0.8", "0.8"],
            "filament_retraction_speed":        ["35", "35"],
            "filament_deretraction_speed":      ["35", "35"],
            "fan_max_speed":                    ["35"],
            "fan_min_speed":                    ["10"],
            "overhang_fan_speed":               ["80"],
            "hot_plate_temp":                   ["100"],
            "hot_plate_temp_initial_layer":     ["100"],
            "textured_plate_temp":              ["100"],
            "textured_plate_temp_initial_layer":["100"],
            "eng_plate_temp":                   ["100"],
            "eng_plate_temp_initial_layer":     ["100"],
            "cool_plate_temp":                  ["0"],
            "cool_plate_temp_initial_layer":    ["0"],
            "filament_start_gcode":             [ASA_START_GCODE],
        },
    },
    {
        # Bambu reference: Bambu TPU 95A on H2S
        "short":         "Inslogic TPU 95A",
        "filament_id":   "Pi3c4d5e6",
        "filament_type": "TPU",
        "nozzles":       ["0.4", "0.6", "0.8"],   # No 0.2mm for TPU
        "settings": {
            "filament_density":                 ["1.22"],
            "temperature_vitrification":        ["30"],
            "nozzle_temperature":               ["230", "230"],
            "nozzle_temperature_initial_layer": ["230", "230"],
            "nozzle_temperature_range_low":     ["210"],
            "nozzle_temperature_range_high":    ["240"],
            "filament_max_volumetric_speed":    ["6", "6"],
            "filament_retraction_length":       ["2.0", "2.0"],
            "filament_retraction_speed":        ["10", "10"],
            "filament_deretraction_speed":      ["10", "10"],
            "fan_max_speed":                    ["100"],
            "fan_min_speed":                    ["100"],
            "overhang_fan_speed":               ["100"],
            "hot_plate_temp":                   ["35"],
            "hot_plate_temp_initial_layer":     ["35"],
            "textured_plate_temp":              ["35"],
            "textured_plate_temp_initial_layer":["35"],
            "eng_plate_temp":                   ["0"],
            "eng_plate_temp_initial_layer":     ["0"],
            "cool_plate_temp":                  ["0"],
            "cool_plate_temp_initial_layer":    ["0"],
        },
    },
    {
        # Bambu reference: Bambu PLA Basic / Generic PLA on H2S
        "short":         "Inslogic Matte PLA",
        "filament_id":   "Pi4d5e6f7",
        "filament_type": "PLA",
        "nozzles":       ["0.2", "0.4", "0.6", "0.8"],
        "settings": {
            "filament_density":                 ["1.24"],
            "temperature_vitrification":        ["60"],
            "nozzle_temperature":               ["220", "220"],
            "nozzle_temperature_initial_layer": ["220", "220"],
            "nozzle_temperature_range_low":     ["190"],
            "nozzle_temperature_range_high":    ["230"],
            "filament_max_volumetric_speed":    ["12", "18"],
            "filament_retraction_length":       ["0.8", "0.8"],
            "filament_retraction_speed":        ["35", "40"],
            "filament_deretraction_speed":      ["35", "40"],
            "fan_max_speed":                    ["100"],
            "fan_min_speed":                    ["100"],
            "overhang_fan_speed":               ["90"],
            "hot_plate_temp":                   ["35"],
            "hot_plate_temp_initial_layer":     ["35"],
            "textured_plate_temp":              ["35"],
            "textured_plate_temp_initial_layer":["35"],
            "eng_plate_temp":                   ["0"],
            "eng_plate_temp_initial_layer":     ["0"],
            "cool_plate_temp":                  ["35"],
            "cool_plate_temp_initial_layer":    ["35"],
            "filament_start_gcode":             [PETG_START_GCODE],
        },
    },
    {
        # Same as PLA but slightly higher temp for toughness additives
        "short":         "Inslogic PLA Pro",
        "filament_id":   "Pi5e6f7a8",
        "filament_type": "PLA",
        "nozzles":       ["0.2", "0.4", "0.6", "0.8"],
        "settings": {
            "filament_density":                 ["1.24"],
            "temperature_vitrification":        ["60"],
            "nozzle_temperature":               ["220", "220"],
            "nozzle_temperature_initial_layer": ["220", "220"],
            "nozzle_temperature_range_low":     ["190"],
            "nozzle_temperature_range_high":    ["235"],
            "filament_max_volumetric_speed":    ["12", "18"],
            "filament_retraction_length":       ["0.8", "0.8"],
            "filament_retraction_speed":        ["35", "40"],
            "filament_deretraction_speed":      ["35", "40"],
            "fan_max_speed":                    ["100"],
            "fan_min_speed":                    ["100"],
            "overhang_fan_speed":               ["90"],
            "hot_plate_temp":                   ["35"],
            "hot_plate_temp_initial_layer":     ["35"],
            "textured_plate_temp":              ["35"],
            "textured_plate_temp_initial_layer":["35"],
            "eng_plate_temp":                   ["0"],
            "eng_plate_temp_initial_layer":     ["0"],
            "cool_plate_temp":                  ["35"],
            "cool_plate_temp_initial_layer":    ["35"],
            "filament_start_gcode":             [PETG_START_GCODE],
        },
    },
    {
        # Silk PLA needs higher temp for proper silk particle flow
        "short":         "Inslogic Silk PLA",
        "filament_id":   "Pi6f7a8b9",
        "filament_type": "PLA",
        "nozzles":       ["0.2", "0.4", "0.6", "0.8"],
        "settings": {
            "filament_density":                 ["1.24"],
            "temperature_vitrification":        ["55"],
            "nozzle_temperature":               ["230", "230"],
            "nozzle_temperature_initial_layer": ["230", "230"],
            "nozzle_temperature_range_low":     ["210"],
            "nozzle_temperature_range_high":    ["240"],
            "filament_max_volumetric_speed":    ["10", "16"],
            "filament_retraction_length":       ["0.8", "0.8"],
            "filament_retraction_speed":        ["35", "40"],
            "filament_deretraction_speed":      ["35", "40"],
            "fan_max_speed":                    ["100"],
            "fan_min_speed":                    ["80"],
            "overhang_fan_speed":               ["90"],
            "hot_plate_temp":                   ["35"],
            "hot_plate_temp_initial_layer":     ["35"],
            "textured_plate_temp":              ["35"],
            "textured_plate_temp_initial_layer":["35"],
            "eng_plate_temp":                   ["0"],
            "eng_plate_temp_initial_layer":     ["0"],
            "cool_plate_temp":                  ["35"],
            "cool_plate_temp_initial_layer":    ["35"],
            "filament_start_gcode":             [PETG_START_GCODE],
        },
    },
    {
        # Nebulux — special effect PLA, same settings as Silk PLA
        "short":         "Inslogic Nebulux PLA",
        "filament_id":   "Pi7a8b9c0",
        "filament_type": "PLA",
        "nozzles":       ["0.2", "0.4", "0.6", "0.8"],
        "settings": {
            "filament_density":                 ["1.24"],
            "temperature_vitrification":        ["55"],
            "nozzle_temperature":               ["225", "225"],
            "nozzle_temperature_initial_layer": ["225", "225"],
            "nozzle_temperature_range_low":     ["210"],
            "nozzle_temperature_range_high":    ["240"],
            "filament_max_volumetric_speed":    ["10", "16"],
            "filament_retraction_length":       ["0.8", "0.8"],
            "filament_retraction_speed":        ["35", "40"],
            "filament_deretraction_speed":      ["35", "40"],
            "fan_max_speed":                    ["100"],
            "fan_min_speed":                    ["80"],
            "overhang_fan_speed":               ["90"],
            "hot_plate_temp":                   ["35"],
            "hot_plate_temp_initial_layer":     ["35"],
            "textured_plate_temp":              ["35"],
            "textured_plate_temp_initial_layer":["35"],
            "eng_plate_temp":                   ["0"],
            "eng_plate_temp_initial_layer":     ["0"],
            "cool_plate_temp":                  ["35"],
            "cool_plate_temp_initial_layer":    ["35"],
            "filament_start_gcode":             [PETG_START_GCODE],
        },
    },
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def gen_sid(prefix: str) -> str:
    return prefix + secrets.token_hex(6)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.write("\n")


def write_info(path: Path, setting_id: str, base_id: str = "", user_id: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join([
        "sync_info = ",
        f"user_id = {user_id}",
        f"setting_id = {setting_id}",
        f"base_id = {base_id}",
        f"updated_time = {TIMESTAMP}",
        "",
    ])
    path.write_text(content, encoding="ascii", newline="\n")


# ─── Builders ─────────────────────────────────────────────────────────────────

def build_filament(fil: dict, template: dict) -> tuple[dict, str]:
    name   = f"my-{fil['short']} @Bambu Lab H2S"
    nozzles = fil.get("nozzles", ["0.2", "0.4", "0.6", "0.8"])
    d = deepcopy(template)
    d["name"]               = name
    d["filament_settings_id"] = [name]
    d["filament_id"]        = fil["filament_id"]
    d["filament_vendor"]    = ["Inslogic"]
    d["filament_type"]      = [fil["filament_type"]]
    d["from"]               = "User"
    d["inherits"]           = ""
    d["version"]            = VERSION
    d["compatible_printers"] = [f"Bambu Lab H2S {nz} nozzle" for nz in nozzles]
    for k, v in fil["settings"].items():
        d[k] = v
    d["enable_pressure_advance"]       = ["1"]
    d["filament_enable_overhang_speed"] = ["0", "0"]
    d["slow_down_layer_time"]          = ["8"]
    return d, gen_sid("PFUS")


def build_preset(fil_name: str, base_sid: str) -> tuple[dict, str]:
    preset = {
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio":       ["nil", "nil"],
        "filament_settings_id":      [fil_name],
        "from":     "User",
        "inherits": fil_name,
        "name":     fil_name,
        "version":  VERSION,
    }
    return preset, gen_sid("PFUS")


def build_calibrated(fil_name: str, base_sid: str) -> tuple[dict, str]:
    cal_name = fil_name.replace("@Bambu Lab H2S", "Calibrated").strip()
    cal = {
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio":       ["nil", "nil"],
        "filament_settings_id":      [cal_name],
        "from":     "User",
        "inherits": fil_name,
        "name":     cal_name,
        "version":  VERSION,
    }
    return cal, gen_sid("PFUS")


def build_process(short: str, nozzle: str) -> tuple[dict, str, str]:
    parent, gp, layer = PROCESS_PARENT[nozzle]
    proc_name = f"my-{short} {layer}mm @H2S {nozzle} nozzle"
    proc = {
        "compatible_printers": [f"Bambu Lab H2S {nozzle} nozzle"],
        "from":           "User",
        "inherits":       parent,
        "instantiation":  "true",
        "name":           proc_name,
        "print_settings_id": proc_name,
        "type":           "process",
        "version":        VERSION,
    }
    return proc, gen_sid("PPUS"), gp


# ─── Generator ────────────────────────────────────────────────────────────────

def generate_filament(fil: dict, template: dict) -> None:
    name = f"my-{fil['short']} @Bambu Lab H2S"

    filament, base_sid = build_filament(fil, template)
    write_json(SCRIPT_DIR / f"{name}.json", filament)
    write_info(SCRIPT_DIR / f"{name}.info", base_sid)

    preset, psid = build_preset(name, base_sid)
    write_json(SCRIPT_DIR / f"{name}.preset.json", preset)
    write_info(SCRIPT_DIR / f"{name}.preset.info", psid, base_id=base_sid, user_id=USER_ID)

    # Calibrated override — kept in repo only, NOT deployed
    cal, cal_sid = build_calibrated(name, base_sid)
    cal_name = cal["name"]
    write_json(SCRIPT_DIR / f"{cal_name}.json", cal)
    write_info(SCRIPT_DIR / f"{cal_name}.info", cal_sid, base_id=base_sid, user_id=USER_ID)

    for nz in fil.get("nozzles", ["0.2", "0.4", "0.6", "0.8"]):
        proc, proc_sid, gp = build_process(fil["short"], nz)
        proc_name = proc["name"]
        write_json(SCRIPT_DIR / f"{proc_name}.json", proc)
        write_info(SCRIPT_DIR / f"{proc_name}.info", proc_sid, base_id=gp, user_id=USER_ID)

    print(f"  generated {fil['short']}")


def copy_to(dest_dirs: list[Path]) -> None:
    for pat in ("my-*.json", "my-*.info", "my-*.preset.json", "my-*.preset.info"):
        for src in SCRIPT_DIR.glob(pat):
            if src.name == "baseline_full_filament.json":
                continue
            if "Calibrated" in src.name:
                continue
            for dest in dest_dirs:
                shutil.copy2(src, dest / src.name)


def main() -> None:
    if not TEMPLATE_PATH.is_file():
        raise SystemExit(f"Missing template: {TEMPLATE_PATH}")
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        template = json.load(f)

    for fil in FILAMENTS:
        generate_filament(fil, template)

    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    copy_to([DEPLOY_DIR])
    print(f"Copied to {DEPLOY_DIR}")


if __name__ == "__main__":
    main()
