"""
Regenerate all process presets using Bambu system profiles as baseline.
Only applies safe, minimal overrides per filament material.

Rules:
- Never use "nil" in speed arrays - always explicit values for both [STD, HF] extruders
- Never override system features (enable_arc_fitting, enable_wrapping_detection, etc.)
- Only override: infill settings, wall_loops, support_top_z_distance, and speeds
- Speed arrays must always have two explicit values [STD, HF]
"""

import json
import os
import random
import time

OUTPUT_DIR_BAMBU = r"C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process"
OUTPUT_DIR_DEPLOY = r"c:\GitHub\filments settings\DeployPack"
REPO_ROOT = r"c:\GitHub\filments settings"

# Mapping from filament name to brand folder in git repo
BRAND_FOLDERS = {
    "Inslogic ASA": r"Inslogic\ASA",
    "Inslogic Matte PLA": r"Inslogic\Matte-PLA",
    "Inslogic PETG Pro": r"Inslogic\PETG-Pro",
    "Inslogic PLA Pro": r"Inslogic\PLA-Pro",
    "Inslogic Silk PLA": r"Inslogic\Silk-PLA",
    "SUNLU PETG HS": r"SUNLU\PETG-HS",
    "SUNLU PA E-PA": r"SUNLU\PA-E-PA",
}

VERSION = "2.6.0.2"

# Bambu system base profiles for H2S nozzles
NOZZLE_PROFILES = {
    "0.2": {"inherits": "0.10mm Standard @BBL H2S 0.2 nozzle", "layer": "0.10mm", "base_id": "GP152"},
    "0.4": {"inherits": "0.20mm Standard @BBL H2S", "layer": "0.20mm", "base_id": "GP158"},
    "0.6": {"inherits": "0.30mm Standard @BBL H2S 0.6 nozzle", "layer": "0.30mm", "base_id": "GP159"},
    "0.8": {"inherits": "0.40mm Standard @BBL H2S 0.8 nozzle", "layer": "0.40mm", "base_id": "GP156"},
}

# Bambu system baseline speeds per nozzle (from actual system profiles)
# Format: [Standard extruder, High Flow extruder]
BAMBU_BASELINE = {
    "0.2": {
        "bridge_speed": ["50", "50"],
        "initial_layer_speed": ["40", "40"],
        "inner_wall_speed": ["150", "150"],
        "outer_wall_speed": ["100", "100"],
        "sparse_infill_speed": ["100", "100"],
        "top_surface_speed": ["150", "150"],
        "support_interface_speed": ["80", "80"],
        "support_speed": ["150", "150"],
    },
    "0.4": {
        "bridge_speed": ["50", "50"],
        "initial_layer_speed": ["50", "50"],
        "inner_wall_speed": ["300", "600"],
        "outer_wall_speed": ["200", "500"],
        "sparse_infill_speed": ["350", "600"],
        "top_surface_speed": ["200", "200"],
        "support_interface_speed": ["80", "80"],
        "support_speed": ["150", "150"],
    },
    "0.6": {
        "bridge_speed": ["30", "30"],
        "initial_layer_speed": ["50", "50"],
        "inner_wall_speed": ["300", "600"],
        "outer_wall_speed": ["120", "500"],
        "sparse_infill_speed": ["350", "600"],
        "top_surface_speed": ["200", "200"],
        "support_interface_speed": ["80", "80"],
        "support_speed": ["150", "150"],
    },
    "0.8": {
        "bridge_speed": ["30", "30"],
        "initial_layer_speed": ["50", "50"],
        "inner_wall_speed": ["300", "600"],
        "outer_wall_speed": ["120", "500"],
        "sparse_infill_speed": ["350", "600"],
        "top_surface_speed": ["200", "200"],
        "support_interface_speed": ["80", "80"],
        "support_speed": ["150", "150"],
    },
}

# Material-specific speed scaling factors (relative to Bambu baseline)
# ASA: slower due to warping/cooling issues, needs careful speed control
# PETG HS: high-speed variant, can run near or at Bambu baseline
# PA E-PA: slowest, nylon needs careful handling
# PLA variants: can run at or near Bambu baseline

FILAMENT_OVERRIDES = {
    "Inslogic PETG Pro": {
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "support_top_z_distance": {
            "0.2": "0.1",
            "0.4": "0.2",
            "0.6": "0.3",
            "0.8": "0.4",
        },
        "speeds": {
            "0.2": {
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["120", "120"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["100", "100"],
                "top_surface_speed": ["100", "100"],
            },
            "0.4": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["220", "220"],
                "outer_wall_speed": ["150", "150"],
                "sparse_infill_speed": ["300", "300"],
                "top_surface_speed": ["200", "200"],
            },
            "0.6": {
                "initial_layer_speed": ["40", "45"],
                "inner_wall_speed": ["250", "300"],
                "outer_wall_speed": ["120", "150"],
                "sparse_infill_speed": ["300", "350"],
                "top_surface_speed": ["200", "200"],
            },
            "0.8": {
                "initial_layer_speed": ["40", "45"],
                "inner_wall_speed": ["250", "300"],
                "outer_wall_speed": ["120", "150"],
                "sparse_infill_speed": ["300", "350"],
                "top_surface_speed": ["200", "200"],
            },
        },
    },
    "Inslogic ASA": {
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "support_top_z_distance": {
            "0.2": "0.1",
            "0.4": "0.2",
            "0.6": "0.2",
            "0.8": "0.2",
        },
        "brim_type": "outer_and_inner",
        "speeds": {
            "0.2": {
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["100", "100"],
                "outer_wall_speed": ["60", "60"],
                "sparse_infill_speed": ["80", "80"],
                "top_surface_speed": ["80", "80"],
            },
            "0.4": {
                "initial_layer_speed": ["35", "35"],
                "inner_wall_speed": ["200", "200"],
                "outer_wall_speed": ["100", "100"],
                "sparse_infill_speed": ["250", "250"],
                "top_surface_speed": ["200", "200"],
            },
            "0.6": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["200", "200"],
                "outer_wall_speed": ["100", "100"],
                "sparse_infill_speed": ["250", "250"],
                "top_surface_speed": ["200", "200"],
            },
            "0.8": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["200", "200"],
                "outer_wall_speed": ["100", "100"],
                "sparse_infill_speed": ["250", "250"],
                "top_surface_speed": ["200", "200"],
            },
        },
    },
    "SUNLU PETG HS": {
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "support_top_z_distance": {
            "0.2": "0.1",
            "0.4": "0.2",
            "0.6": "0.3",
            "0.8": "0.4",
        },
        "speeds": {
            "0.2": {
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["120", "120"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["100", "100"],
                "top_surface_speed": ["100", "100"],
            },
            "0.4": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["220", "220"],
                "outer_wall_speed": ["150", "150"],
                "sparse_infill_speed": ["300", "300"],
                "top_surface_speed": ["200", "200"],
            },
            "0.6": {
                "initial_layer_speed": ["40", "45"],
                "inner_wall_speed": ["250", "300"],
                "outer_wall_speed": ["120", "150"],
                "sparse_infill_speed": ["300", "350"],
                "top_surface_speed": ["200", "200"],
            },
            "0.8": {
                "initial_layer_speed": ["40", "45"],
                "inner_wall_speed": ["250", "300"],
                "outer_wall_speed": ["120", "150"],
                "sparse_infill_speed": ["300", "350"],
                "top_surface_speed": ["200", "200"],
            },
        },
    },
    "SUNLU PA E-PA": {
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "support_top_z_distance": {
            "0.2": "0.1",
            "0.4": "0.2",
            "0.6": "0.3",
            "0.8": "0.4",
        },
        "speeds": {
            "0.2": {
                "bridge_speed": ["20", "20"],
                "initial_layer_speed": ["25", "25"],
                "inner_wall_speed": ["80", "80"],
                "outer_wall_speed": ["50", "50"],
                "sparse_infill_speed": ["80", "80"],
                "top_surface_speed": ["60", "60"],
            },
            "0.4": {
                "bridge_speed": ["20", "20"],
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["130", "130"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["160", "160"],
                "top_surface_speed": ["200", "200"],
            },
            "0.6": {
                "bridge_speed": ["20", "20"],
                "initial_layer_speed": ["35", "35"],
                "inner_wall_speed": ["160", "160"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["200", "200"],
                "top_surface_speed": ["200", "200"],
            },
            "0.8": {
                "bridge_speed": ["20", "20"],
                "initial_layer_speed": ["35", "35"],
                "inner_wall_speed": ["160", "160"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["200", "200"],
                "top_surface_speed": ["200", "200"],
            },
        },
    },
    "Inslogic Matte PLA": {
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "support_top_z_distance": {
            "0.2": "0.1",
            "0.4": "0.2",
            "0.6": "0.3",
            "0.8": "0.4",
        },
        "speeds": {
            "0.2": {
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["100", "100"],
                "outer_wall_speed": ["60", "60"],
                "sparse_infill_speed": ["100", "100"],
                "top_surface_speed": ["80", "80"],
            },
            "0.4": {
                "initial_layer_speed": ["35", "35"],
                "inner_wall_speed": ["200", "200"],
                "outer_wall_speed": ["100", "100"],
                "sparse_infill_speed": ["250", "250"],
                "top_surface_speed": ["200", "200"],
            },
            "0.6": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["250", "250"],
                "outer_wall_speed": ["100", "100"],
                "sparse_infill_speed": ["280", "280"],
                "top_surface_speed": ["200", "200"],
            },
            "0.8": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["250", "250"],
                "outer_wall_speed": ["100", "100"],
                "sparse_infill_speed": ["280", "280"],
                "top_surface_speed": ["200", "200"],
            },
        },
    },
    "Inslogic PLA Pro": {
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "support_top_z_distance": {
            "0.2": "0.1",
            "0.4": "0.2",
            "0.6": "0.3",
            "0.8": "0.4",
        },
        "speeds": {
            "0.2": {
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["120", "120"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["100", "100"],
                "top_surface_speed": ["100", "100"],
            },
            "0.4": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["250", "250"],
                "outer_wall_speed": ["150", "150"],
                "sparse_infill_speed": ["300", "300"],
                "top_surface_speed": ["200", "200"],
            },
            "0.6": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["280", "280"],
                "outer_wall_speed": ["120", "120"],
                "sparse_infill_speed": ["300", "300"],
                "top_surface_speed": ["200", "200"],
            },
            "0.8": {
                "initial_layer_speed": ["40", "40"],
                "inner_wall_speed": ["280", "280"],
                "outer_wall_speed": ["120", "120"],
                "sparse_infill_speed": ["300", "300"],
                "top_surface_speed": ["200", "200"],
            },
        },
    },
    "Inslogic Silk PLA": {
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "support_top_z_distance": {
            "0.2": "0.1",
            "0.4": "0.2",
            "0.6": "0.3",
            "0.8": "0.4",
        },
        "speeds": {
            "0.2": {
                "bridge_speed": ["25", "25"],
                "initial_layer_speed": ["25", "25"],
                "inner_wall_speed": ["80", "80"],
                "outer_wall_speed": ["50", "50"],
                "sparse_infill_speed": ["80", "80"],
                "top_surface_speed": ["60", "60"],
            },
            "0.4": {
                "bridge_speed": ["25", "25"],
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["120", "120"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["150", "150"],
                "top_surface_speed": ["200", "200"],
            },
            "0.6": {
                "bridge_speed": ["25", "25"],
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["150", "150"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["180", "180"],
                "top_surface_speed": ["200", "200"],
            },
            "0.8": {
                "bridge_speed": ["25", "25"],
                "initial_layer_speed": ["30", "30"],
                "inner_wall_speed": ["150", "150"],
                "outer_wall_speed": ["80", "80"],
                "sparse_infill_speed": ["180", "180"],
                "top_surface_speed": ["200", "200"],
            },
        },
    },
}


def gen_setting_id():
    return "PPUS" + "".join(random.choice("0123456789abcdef") for _ in range(12))


def gen_info(setting_id, base_id):
    ts = int(time.time())
    return f"sync_info = \nuser_id = 2189385007\nsetting_id = {setting_id}\nbase_id = {base_id}\nupdated_time = {ts}\n"


def build_preset(filament_name, nozzle):
    """Build a clean process preset JSON dict."""
    nozzle_cfg = NOZZLE_PROFILES[nozzle]
    overrides = FILAMENT_OVERRIDES[filament_name]

    name = f"my-{filament_name} {nozzle_cfg['layer']} @H2S {nozzle} nozzle"

    preset = {}

    # Add speed overrides from material config (these are the ONLY speed fields we set)
    speeds = overrides["speeds"][nozzle]
    for key in sorted(speeds.keys()):
        preset[key] = speeds[key]

    # Add brim_type if specified (ASA)
    if "brim_type" in overrides:
        preset["brim_type"] = overrides["brim_type"]

    preset["enable_support"] = "1"
    preset["from"] = "User"
    preset["inherits"] = nozzle_cfg["inherits"]
    preset["name"] = name

    preset["print_extruder_id"] = ["1", "1"]
    preset["print_extruder_variant"] = ["Direct Drive Standard", "Direct Drive High Flow"]
    preset["print_settings_id"] = name

    preset["sparse_infill_density"] = overrides["sparse_infill_density"]
    preset["sparse_infill_pattern"] = overrides["sparse_infill_pattern"]

    # Support Z distance per nozzle
    support_z = overrides["support_top_z_distance"][nozzle]
    preset["support_top_z_distance"] = support_z

    preset["version"] = VERSION
    preset["wall_loops"] = overrides["wall_loops"]

    # Compatible printers - required for BambuStudio to load properly
    compatible_printers_map = {
        "0.2": "Bambu Lab H2S 0.2 nozzle",
        "0.4": "Bambu Lab H2S 0.4 nozzle",
        "0.6": "Bambu Lab H2S 0.6 nozzle",
        "0.8": "Bambu Lab H2S 0.8 nozzle",
    }
    preset["compatible_printers"] = [compatible_printers_map[nozzle]]

    return preset


def read_existing_info(filepath):
    """Read existing .info file and return setting_id if it exists."""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("setting_id = "):
                    return line.strip().split(" = ", 1)[1]
    return None


def write_preset(json_content, info_content, json_filename, info_filename, output_dir):
    """Write JSON and info files to a directory."""
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, json_filename)
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(json_content, f, indent=4, sort_keys=True)
        f.write("\n")

    info_path = os.path.join(output_dir, info_filename)
    with open(info_path, "w", encoding="ascii", newline="\n") as f:
        f.write(info_content)


def main():
    os.makedirs(OUTPUT_DIR_BAMBU, exist_ok=True)
    os.makedirs(OUTPUT_DIR_DEPLOY, exist_ok=True)

    count = 0
    for filament_name in sorted(FILAMENT_OVERRIDES.keys()):
        for nozzle in ["0.2", "0.4", "0.6", "0.8"]:
            nozzle_cfg = NOZZLE_PROFILES[nozzle]
            preset = build_preset(filament_name, nozzle)
            name = preset["name"]

            json_filename = f"{name}.json"
            info_filename = f"{name}.info"

            # Check if existing info file has a setting_id we should preserve
            existing_info_path = os.path.join(OUTPUT_DIR_BAMBU, info_filename)
            existing_id = read_existing_info(existing_info_path)
            setting_id = existing_id if existing_id else gen_setting_id()

            info_content = gen_info(setting_id, nozzle_cfg["base_id"])

            # Write to BambuStudio process folder
            write_preset(preset, info_content, json_filename, info_filename, OUTPUT_DIR_BAMBU)

            # Write to DeployPack
            write_preset(preset, info_content, json_filename, info_filename, OUTPUT_DIR_DEPLOY)

            # Write to brand folder in git repo (if it exists)
            if filament_name in BRAND_FOLDERS:
                brand_dir = os.path.join(REPO_ROOT, BRAND_FOLDERS[filament_name])
                if os.path.isdir(brand_dir):
                    write_preset(preset, info_content, json_filename, info_filename, brand_dir)

            count += 1
            print(f"  [{count:2d}] {name}")

    print(f"\nGenerated {count} process presets in:")
    print(f"  {OUTPUT_DIR_BAMBU}")
    print(f"  + brand folders in {REPO_ROOT}")


if __name__ == "__main__":
    main()
