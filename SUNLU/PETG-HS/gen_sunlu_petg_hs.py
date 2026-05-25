#!/usr/bin/env python3
"""
Generate SUNLU filament profiles for Bambu Lab H2S.

Produces:
  - SUNLU PETG HS   (High Speed Matte PETG)
  - SUNLU PETG      (Standard PETG)
  - SUNLU TPU 95A   (TPU 95A Shore — no 0.2mm nozzle)
  - SUNLU PA E-PA   (Easy Nylon 6+66 — requires glue on textured PEI)

Design: ONE filament file per product that lists compatible H2S nozzle sizes in
compatible_printers — identical behaviour to Bambu's built-in presets.
No need to reassign the filament when changing nozzle size.

Rules (see .cursor/rules/add-filament.mdc):
- Fan speeds matched to Bambu system profile for each material type.
- enable_pressure_advance on; retraction speeds never nil.
- Process presets inherit ONLY Bambu Standard.
- Calibrated preset kept in repo but NOT deployed (avoids duplicate dropdown entries).
"""

from __future__ import annotations

import json
import secrets
import shutil
import time
from copy import deepcopy
from pathlib import Path

VERSION = "2.6.0.2"
USER_ID = "2189385007"
TIMESTAMP = str(int(time.time()))

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEPLOY_DIR = REPO_ROOT / "DeployPack"
TEMPLATE_PATH = SCRIPT_DIR / "baseline_full_filament.json"

ALL_H2S_NOZZLES = [
    "Bambu Lab H2S 0.2 nozzle",
    "Bambu Lab H2S 0.4 nozzle",
    "Bambu Lab H2S 0.6 nozzle",
    "Bambu Lab H2S 0.8 nozzle",
]

# Bambu system process parents (H2S)
PROCESS_PARENT = {
    "0.2": ("0.10mm Standard @BBL H2S 0.2 nozzle", "GP152", "0.10"),
    "0.4": ("0.20mm Standard @BBL H2S",             "GP158", "0.20"),
    "0.6": ("0.30mm Standard @BBL H2S 0.6 nozzle",  "GP159", "0.30"),
    "0.8": ("0.40mm Standard @BBL H2S 0.8 nozzle",  "GP156", "0.40"),
}

# ─── Filament definitions ─────────────────────────────────────────────────────
# Each entry also carries material-specific fan / gcode overrides via "overrides".
# "nozzles" defaults to all four; set explicitly to exclude sizes (e.g. TPU no 0.2).

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

FILAMENTS = [
    {
        "short":       "SUNLU PETG HS",
        "filament_id": "P759ffa0",
        "filament_type": "PETG",
        "nozzles": ["0.2", "0.4", "0.6", "0.8"],
        # High-speed matte PETG — TDS: 240-260°C, density 1.28, Tg 65.5°C
        "settings": {
            "filament_density":                ["1.28"],
            "temperature_vitrification":       ["65"],
            "nozzle_temperature":              ["245", "255"],
            "nozzle_temperature_initial_layer":["250", "260"],
            "nozzle_temperature_range_low":    ["235"],
            "nozzle_temperature_range_high":   ["270"],
            "filament_max_volumetric_speed":   ["18", "28"],
            "filament_retraction_length":      ["1.0", "1.0"],
            "filament_retraction_speed":       ["35", "40"],
            "filament_deretraction_speed":     ["35", "40"],
            # PETG fan: 60/20/50% (Bambu baseline — prevents stringing)
            "fan_max_speed":                   ["60"],
            "fan_min_speed":                   ["20"],
            "overhang_fan_speed":              ["50"],
            "filament_start_gcode":            [PETG_START_GCODE],
        },
    },
    {
        "short":       "SUNLU PETG",
        "filament_id": "Pf8c2d4a1",
        "filament_type": "PETG",
        "nozzles": ["0.2", "0.4", "0.6", "0.8"],
        # Standard PETG — TDS: 230-250°C, density 1.27, Tg 79°C
        "settings": {
            "filament_density":                ["1.27"],
            "temperature_vitrification":       ["79"],
            "nozzle_temperature":              ["240", "245"],
            "nozzle_temperature_initial_layer":["240", "245"],
            "nozzle_temperature_range_low":    ["230"],
            "nozzle_temperature_range_high":   ["255"],
            "filament_max_volumetric_speed":   ["12", "18"],
            "filament_retraction_length":      ["0.8", "0.8"],
            "filament_retraction_speed":       ["35", "35"],
            "filament_deretraction_speed":     ["35", "35"],
            "fan_max_speed":                   ["60"],
            "fan_min_speed":                   ["20"],
            "overhang_fan_speed":              ["50"],
            "filament_start_gcode":            [PETG_START_GCODE],
        },
    },
    {
        "short":       "SUNLU TPU 95A",
        "filament_id": "Pe5a1b7c2",
        "filament_type": "TPU",
        "nozzles": ["0.4", "0.6", "0.8"],   # No 0.2mm for TPU
        # TPU 95A — TDS: 210-230°C, bed 35°C, density 1.22, Tg 30°C
        # Fan: Bambu TPU baseline 100/100% (TPU needs cooling for bridging)
        "settings": {
            "filament_density":                ["1.22"],
            "temperature_vitrification":       ["30"],
            "nozzle_temperature":              ["230", "230"],
            "nozzle_temperature_initial_layer":["230", "230"],
            "nozzle_temperature_range_low":    ["210"],
            "nozzle_temperature_range_high":   ["240"],
            "filament_max_volumetric_speed":   ["6", "6"],
            "filament_retraction_length":      ["2.0", "2.0"],
            "filament_retraction_speed":       ["10", "10"],
            "filament_deretraction_speed":     ["10", "10"],
            "fan_max_speed":                   ["100"],
            "fan_min_speed":                   ["100"],
            "overhang_fan_speed":              ["100"],
            "hot_plate_temp":                  ["35"],
            "hot_plate_temp_initial_layer":    ["35"],
            "textured_plate_temp":             ["35"],
            "textured_plate_temp_initial_layer":["35"],
            "eng_plate_temp":                  ["0"],
            "eng_plate_temp_initial_layer":    ["0"],
            "cool_plate_temp":                 ["0"],
            "cool_plate_temp_initial_layer":   ["0"],
        },
    },
    {
        "short":       "SUNLU PLA",
        "filament_id": "Pb3c1a5f2",
        "filament_type": "PLA",
        "nozzles": ["0.2", "0.4", "0.6", "0.8"],
        # Standard PLA — TDS: 190-220°C, bed 35-60°C, density 1.24, Tg 60°C
        # Fan: Bambu PLA baseline 100/100%
        "settings": {
            "filament_density":                ["1.24"],
            "temperature_vitrification":       ["60"],
            "nozzle_temperature":              ["220", "220"],
            "nozzle_temperature_initial_layer":["220", "220"],
            "nozzle_temperature_range_low":    ["190"],
            "nozzle_temperature_range_high":   ["230"],
            "filament_max_volumetric_speed":   ["12", "18"],
            "filament_retraction_length":      ["0.8", "0.8"],
            "filament_retraction_speed":       ["35", "40"],
            "filament_deretraction_speed":     ["35", "40"],
            "fan_max_speed":                   ["100"],
            "fan_min_speed":                   ["100"],
            "overhang_fan_speed":              ["90"],
            "hot_plate_temp":                  ["35"],
            "hot_plate_temp_initial_layer":    ["35"],
            "textured_plate_temp":             ["35"],
            "textured_plate_temp_initial_layer":["35"],
            "eng_plate_temp":                  ["0"],
            "eng_plate_temp_initial_layer":    ["0"],
            "cool_plate_temp":                 ["35"],
            "cool_plate_temp_initial_layer":   ["35"],
            "filament_start_gcode":            [PETG_START_GCODE],
        },
    },
    {
        "short":       "SUNLU PA E-PA",
        "filament_id": "Pa7e3c19",
        "filament_type": "PA",
        "nozzles": ["0.2", "0.4", "0.6", "0.8"],
        # Easy Nylon 6+66 — TDS: 260-280°C, bed 50°C (textured PEI + glue)
        # Fan: Bambu PA baseline 30/10/50%
        "settings": {
            "filament_density":                ["1.10"],
            "temperature_vitrification":       ["65"],
            "nozzle_temperature":              ["265", "265"],
            "nozzle_temperature_initial_layer":["270", "270"],
            "nozzle_temperature_range_low":    ["255"],
            "nozzle_temperature_range_high":   ["280"],
            "filament_max_volumetric_speed":   ["9", "12"],
            "filament_retraction_length":      ["1.0", "1.0"],
            "filament_retraction_speed":       ["35", "35"],
            "filament_deretraction_speed":     ["35", "35"],
            "fan_max_speed":                   ["30"],
            "fan_min_speed":                   ["10"],
            "overhang_fan_speed":              ["50"],
            "hot_plate_temp":                  ["50"],
            "hot_plate_temp_initial_layer":    ["50"],
            "textured_plate_temp":             ["50"],
            "textured_plate_temp_initial_layer":["50"],
            "eng_plate_temp":                  ["50"],
            "eng_plate_temp_initial_layer":    ["50"],
            "cool_plate_temp":                 ["0"],
            "cool_plate_temp_initial_layer":   ["0"],
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
    """Full filament JSON listing compatible H2S nozzle sizes."""
    name = f"{fil['short']} @Bambu Lab H2S"
    nozzles = fil.get("nozzles", ["0.2", "0.4", "0.6", "0.8"])
    d = deepcopy(template)
    d["name"] = name
    d["filament_settings_id"] = [name]
    d["filament_id"] = fil["filament_id"]
    d["filament_vendor"] = ["SUNLU"]
    d["filament_type"] = [fil["filament_type"]]
    d["from"] = "User"
    d["inherits"] = ""
    d["version"] = VERSION
    d["compatible_printers"] = [f"Bambu Lab H2S {nz} nozzle" for nz in nozzles]
    # Apply all filament-specific settings (temps, fans, retraction, bed, gcode…)
    for k, v in fil["settings"].items():
        d[k] = v
    # Always-on fields
    d["enable_pressure_advance"] = ["1"]
    d["filament_enable_overhang_speed"] = ["0", "0"]
    d["slow_down_layer_time"] = ["8"]
    return d, gen_sid("PFUS")


def build_preset(fil_name: str, base_sid: str) -> tuple[dict, str]:
    preset = {
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio": ["nil", "nil"],
        "filament_settings_id": [fil_name],
        "from": "User",
        "inherits": fil_name,
        "name": fil_name,
        "version": VERSION,
    }
    return preset, gen_sid("PFUS")


def build_calibrated(fil_name: str, base_sid: str) -> tuple[dict, str]:
    cal_name = fil_name.replace("@Bambu Lab H2S", "Calibrated").strip()
    cal = {
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio": ["nil", "nil"],
        "filament_settings_id": [cal_name],
        "from": "User",
        "inherits": fil_name,
        "name": cal_name,
        "version": VERSION,
    }
    return cal, gen_sid("PFUS")


def build_process(short: str, nozzle: str) -> tuple[dict, str, str]:
    parent, gp, layer = PROCESS_PARENT[nozzle]
    proc_name = f"{short} {layer}mm @H2S {nozzle} nozzle"
    proc = {
        "compatible_printers": [f"Bambu Lab H2S {nozzle} nozzle"],
        "from": "User",
        "inherits": parent,
        "instantiation": "true",
        "name": proc_name,
        "print_settings_id": proc_name,
        "type": "process",
        "version": VERSION,
    }
    return proc, gen_sid("PPUS"), gp

# ─── Generator ────────────────────────────────────────────────────────────────

def generate_filament(fil: dict, template: dict) -> None:
    name = f"{fil['short']} @Bambu Lab H2S"

    filament, base_sid = build_filament(fil, template)
    write_json(SCRIPT_DIR / f"{name}.json", filament)
    write_info(SCRIPT_DIR / f"{name}.info", base_sid)

    preset, psid = build_preset(name, base_sid)
    write_json(SCRIPT_DIR / f"{name}.preset.json", preset)
    write_info(SCRIPT_DIR / f"{name}.preset.info", psid, base_id=base_sid, user_id=USER_ID)

    # Calibrated override — kept in repo but NOT deployed to filament/ by default
    # (avoids duplicate entries in Bambu Studio filament dropdown).
    # Deploy manually if you want to use it for flow ratio overrides.
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
    for pat in ("*.json", "*.info", "*.preset.json", "*.preset.info"):
        for src in SCRIPT_DIR.glob(pat):
            if src.name == "baseline_full_filament.json":
                continue
            # Skip Calibrated — kept in repo only, not deployed
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
