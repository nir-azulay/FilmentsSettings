"""
Generate ALL SUNLU filament profiles for Bambu Lab H2S.

Strategy: Use Bambu system profiles as the EXACT baseline.
Only override what's absolutely necessary:
  - name, filament_id, filament_settings_id (identity)
  - filament_density, temperature_vitrification (from TDS)
  - from: "User" (required for user profiles)
  - version (match current BambuStudio)

Everything else (temps, speeds, fans, retraction, gcode) is inherited
from the Bambu system profile unchanged.
"""

import json
import os
import secrets
import time
import shutil

VERSION = "2.6.0.2"
USER_ID = "2189385007"
TIMESTAMP = str(int(time.time()))

REPO_ROOT = r"c:\GitHub\filments settings"
DEPLOY_DIR = os.path.join(REPO_ROOT, "DeployPack")

# Bambu system profile names that our profiles inherit from
# These are the H2S-specific profiles (which themselves inherit from @base -> fdm_filament_*)
BAMBU_PETG_SYSTEM = {
    "0.2": "Generic PETG @BBL H2S 0.2 nozzle",
    "0.4": "Generic PETG @BBL H2S",
    "0.6": "Generic PETG @BBL H2S",
    "0.8": "Generic PETG @BBL H2S",
}

BAMBU_PETG_HF_SYSTEM = {
    "0.2": "Generic PETG HF @BBL H2S 0.2 nozzle",
    "0.4": "Generic PETG HF @BBL H2S 0.4 nozzle",
    "0.6": "Generic PETG HF @BBL H2S 0.4 nozzle",
    "0.8": "Generic PETG HF @BBL H2S 0.4 nozzle",
}

BAMBU_PA_SYSTEM = {
    "0.2": "Generic PA @BBL H2S 0.4 nozzle",  # No 0.2 specific PA profile exists
    "0.4": "Generic PA @BBL H2S 0.4 nozzle",
    "0.6": "Generic PA @BBL H2S 0.4 nozzle",
    "0.8": "Generic PA @BBL H2S 0.4 nozzle",
}

BAMBU_TPU_SYSTEM = {
    "0.4": "Bambu TPU 95A @BBL H2S",
    "0.6": "Bambu TPU 95A @BBL H2S",
    "0.8": "Bambu TPU 95A @BBL H2S",
}

# Process system profiles to inherit from
PROCESS_SYSTEM = {
    "0.2": {"name": "0.10mm Standard @BBL H2S 0.2 nozzle", "id": "GP152", "layer": "0.10"},
    "0.4": {"name": "0.20mm Standard @BBL H2S", "id": "GP158", "layer": "0.20"},
    "0.6": {"name": "0.30mm Standard @BBL H2S 0.6 nozzle", "id": "GP159", "layer": "0.30"},
    "0.8": {"name": "0.40mm Standard @BBL H2S 0.8 nozzle", "id": "GP156", "layer": "0.40"},
}

NOZZLE_SUFFIX = {
    "0.2": " 0.2 nozzle",
    "0.4": " 0.4 nozzle",
    "0.6": " 0.6 nozzle",
    "0.8": " 0.8 nozzle",
}

COMPATIBLE_PRINTERS = {
    "0.2": ["Bambu Lab H2S 0.2 nozzle"],
    "0.4": ["Bambu Lab H2S 0.4 nozzle"],
    "0.6": ["Bambu Lab H2S 0.6 nozzle"],
    "0.8": ["Bambu Lab H2S 0.8 nozzle"],
}


def gen_setting_id(prefix="PFUS"):
    return prefix + secrets.token_hex(6)


def write_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.write("\n")
    print(f"  wrote {os.path.basename(path)}")


def write_info(path, setting_id, base_id="", user_id="", prefix="PFUS"):
    content = (
        f"sync_info = \n"
        f"user_id = {user_id}\n"
        f"setting_id = {setting_id}\n"
        f"base_id = {base_id}\n"
        f"updated_time = {TIMESTAMP}\n"
    )
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(content)
    print(f"  wrote {os.path.basename(path)}")


# ============================================================================
# FILAMENT DEFINITIONS - only TDS-specific overrides from Bambu baseline
# ============================================================================

FILAMENTS = [
    {
        "short_name": "SUNLU PETG HS",
        "folder": os.path.join(REPO_ROOT, "SUNLU", "PETG-HS"),
        "filament_id": "P759ffa0",
        "base_system": BAMBU_PETG_HF_SYSTEM,  # High-speed PETG -> use PETG HF baseline
        "nozzles": ["0.2", "0.4", "0.6", "0.8"],
        "overrides": {
            "filament_density": ["1.28"],
            "temperature_vitrification": ["65"],
        },
    },
    {
        "short_name": "SUNLU PETG",
        "folder": os.path.join(REPO_ROOT, "SUNLU", "PETG"),
        "filament_id": "Pf8c2d4a1",
        "base_system": BAMBU_PETG_SYSTEM,  # Standard PETG -> use Generic PETG baseline
        "nozzles": ["0.2", "0.4", "0.6", "0.8"],
        "overrides": {
            "filament_density": ["1.27"],
            "temperature_vitrification": ["79"],
        },
    },
    {
        "short_name": "SUNLU PA E-PA",
        "folder": os.path.join(REPO_ROOT, "SUNLU", "PA-E-PA"),
        "filament_id": "Pa7e3c19",
        "base_system": BAMBU_PA_SYSTEM,
        "nozzles": ["0.2", "0.4", "0.6", "0.8"],
        "overrides": {
            "filament_density": ["1.10"],
            "temperature_vitrification": ["65"],
        },
    },
    {
        "short_name": "SUNLU TPU 95A",
        "folder": os.path.join(REPO_ROOT, "SUNLU", "TPU-95A"),
        "filament_id": "Pe5a1b7c2",
        "base_system": BAMBU_TPU_SYSTEM,
        "nozzles": ["0.4", "0.6", "0.8"],  # No 0.2mm for TPU
        "overrides": {
            "filament_density": ["1.22"],
            "temperature_vitrification": ["30"],
        },
    },
]


def generate_filament(fil):
    """Generate all profile files for one filament."""
    folder = fil["folder"]
    os.makedirs(folder, exist_ok=True)

    short = fil["short_name"]
    fid = fil["filament_id"]
    nozzles = fil["nozzles"]
    overrides = fil["overrides"]
    base_system = fil["base_system"]

    base_info_ids = {}

    print(f"\n=== {short} ===")

    # --- 1. Base filament profiles (filament/base/) ---
    for nz in nozzles:
        profile_name = f"my-{short} @Bambu Lab H2S{NOZZLE_SUFFIX[nz]}"
        inherits = base_system[nz]

        profile = {
            "type": "filament",
            "name": profile_name,
            "inherits": inherits,
            "from": "User",
            "filament_id": fid,
            "instantiation": "true",
            "version": VERSION,
            "compatible_printers": COMPATIBLE_PRINTERS[nz],
        }

        # Apply only TDS-specific overrides
        for key, val in overrides.items():
            profile[key] = val

        json_path = os.path.join(folder, f"{profile_name}.json")
        write_json(json_path, profile)

        sid = gen_setting_id("PFUS")
        base_info_ids[nz] = sid
        info_path = os.path.join(folder, f"{profile_name}.info")
        write_info(info_path, sid)

    # --- 2. User preset files (filament/) - sparse, inheriting ---
    for nz in nozzles:
        profile_name = f"my-{short} @Bambu Lab H2S{NOZZLE_SUFFIX[nz]}"
        preset = {
            "filament_settings_id": [profile_name],
            "from": "User",
            "inherits": profile_name,
            "name": profile_name,
            "version": VERSION,
        }

        preset_path = os.path.join(folder, f"{profile_name}.preset.json")
        write_json(preset_path, preset)

        sid = gen_setting_id("PFUS")
        preset_info_path = os.path.join(folder, f"{profile_name}.preset.info")
        write_info(preset_info_path, sid, base_id=base_info_ids[nz], user_id=USER_ID)

    # --- 3. Calibrated override (filament/) ---
    cal_name = f"my-{short} Calibrated"
    default_nz = "0.4" if "0.4" in nozzles else nozzles[0]
    base_name = f"my-{short} @Bambu Lab H2S{NOZZLE_SUFFIX[default_nz]}"

    calibrated = {
        "filament_settings_id": [cal_name],
        "from": "User",
        "inherits": base_name,
        "name": cal_name,
        "version": VERSION,
    }

    cal_json_path = os.path.join(folder, f"{cal_name}.json")
    write_json(cal_json_path, calibrated)

    sid = gen_setting_id("PFUS")
    cal_info_path = os.path.join(folder, f"{cal_name}.info")
    write_info(cal_info_path, sid, base_id=base_info_ids[default_nz], user_id=USER_ID)

    # --- 4. Process presets (process/) ---
    for nz in nozzles:
        proc_sys = PROCESS_SYSTEM[nz]
        proc_name = f"my-{short} {proc_sys['layer']}mm @H2S{NOZZLE_SUFFIX[nz]}"

        process = {
            "type": "process",
            "name": proc_name,
            "inherits": proc_sys["name"],
            "from": "User",
            "instantiation": "true",
            "version": VERSION,
            "sparse_infill_pattern": "gyroid",
            "sparse_infill_density": "20%",
            "wall_loops": "4",
            "compatible_printers": COMPATIBLE_PRINTERS[nz],
        }

        proc_json_path = os.path.join(folder, f"{proc_name}.json")
        write_json(proc_json_path, process)

        sid = gen_setting_id("PPUS")
        proc_info_path = os.path.join(folder, f"{proc_name}.info")
        write_info(proc_info_path, sid, base_id=proc_sys["id"], user_id=USER_ID)


def copy_to_deploypack():
    """Copy all generated files to the flat DeployPack folder."""
    print(f"\n=== Copying to DeployPack ===")
    os.makedirs(DEPLOY_DIR, exist_ok=True)

    count = 0
    for fil in FILAMENTS:
        folder = fil["folder"]
        for f in os.listdir(folder):
            if f.startswith("my-") and (f.endswith(".json") or f.endswith(".info")):
                src = os.path.join(folder, f)
                dst = os.path.join(DEPLOY_DIR, f)
                shutil.copy2(src, dst)
                count += 1

    print(f"  Copied {count} files to DeployPack")


if __name__ == "__main__":
    for fil in FILAMENTS:
        generate_filament(fil)

    copy_to_deploypack()
    print("\nDone! All SUNLU profiles generated.")
