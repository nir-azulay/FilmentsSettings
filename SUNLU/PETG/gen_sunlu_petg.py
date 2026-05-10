"""Generate SUNLU PETG (standard) filament profiles for Bambu Lab H2S.

Inherits from Bambu system profiles:
- 0.2 nozzle: Generic PETG @BBL H2S 0.2 nozzle
- 0.4/0.6/0.8 nozzle: Generic PETG @BBL H2S
"""
import json
import os
import random
import shutil
import time

BRAND = "SUNLU"
MATERIAL = "PETG"
FILAMENT_ID = "Pf8c2d4a1"
FILAMENT_TYPE = "PETG"
VERSION = "2.6.0.2"

NOZZLE_SIZES = ["0.2", "0.4", "0.6", "0.8"]

INHERITS_MAP = {
    "0.2": "Generic PETG @BBL H2S 0.2 nozzle",
    "0.4": "Generic PETG @BBL H2S",
    "0.6": "Generic PETG @BBL H2S",
    "0.8": "Generic PETG @BBL H2S",
}

NOZZLE_PRINTERS = {
    "0.2": "Bambu Lab H2S 0.2 nozzle",
    "0.4": "Bambu Lab H2S 0.4 nozzle",
    "0.6": "Bambu Lab H2S 0.6 nozzle",
    "0.8": "Bambu Lab H2S 0.8 nozzle",
}

# SUNLU PETG standard specs:
# Nozzle: 230-260°C (230-240 for 50-100mm/s, 240-260 for 100-200mm/s)
# Bed: 60-70°C
# Density: ~1.27 g/cm³ (standard PETG)
# Tolerance: ±0.02mm

BASE_OVERRIDES = {
    "filament_cost": ["45.00"],
    "filament_density": ["1.27"],
    "filament_deretraction_speed": ["35", "35"],
    "filament_dev_ams_drying_heat_distortion_temperature": ["70"],
    "filament_end_gcode": ["; filament end gcode \n\n"],
    "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
    "filament_flow_ratio": ["1", "1"],
    "filament_id": FILAMENT_ID,
    "filament_max_volumetric_speed": ["12", "18"],
    "filament_type": ["PETG"],
    "filament_retraction_length": ["0.8", "0.8"],
    "filament_retraction_speed": ["35", "35"],
    "filament_start_gcode": ["; filament start gcode\n{if (bed_temperature[current_extruder] >80)||(bed_temperature_initial_layer[current_extruder] >80)}M106 P3 S255\n{elsif (bed_temperature[current_extruder] >60)||(bed_temperature_initial_layer[current_extruder] >60)}M106 P3 S180\n{endif}\n\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"],
    "filament_vendor": [BRAND],
    "from": "User",
    "nozzle_temperature": ["240", "245"],
    "nozzle_temperature_initial_layer": ["240", "245"],
    "temperature_vitrification": ["79"],
    "version": VERSION,
}

OVERRIDES_02 = dict(BASE_OVERRIDES)
OVERRIDES_02["filament_max_volumetric_speed"] = ["1", "1"]

PROCESS_INHERITS = {
    "0.2": "0.10mm Standard @BBL H2S 0.2 nozzle",
    "0.4": "0.20mm Standard @BBL H2S",
    "0.6": "0.30mm Standard @BBL H2S 0.6 nozzle",
    "0.8": "0.40mm Standard @BBL H2S 0.8 nozzle",
}

PROCESS_BASE_IDS = {
    "0.2": "GP152",
    "0.4": "GP158",
    "0.6": "GP159",
    "0.8": "GP156",
}

LAYER_HEIGHTS = {
    "0.2": "0.10",
    "0.4": "0.20",
    "0.6": "0.30",
    "0.8": "0.40",
}

PROCESS_OVERRIDES = {
    "0.2": {
        "compatible_printers": ["Bambu Lab H2S 0.2 nozzle"],
        "initial_layer_speed": ["30", "30"],
        "inner_wall_speed": ["80", "100"],
        "outer_wall_speed": ["60", "80"],
        "print_extruder_id": ["1", "1"],
        "print_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "sparse_infill_speed": ["120", "150"],
        "top_surface_speed": ["60", "80"],
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "enable_support": "1",
        "support_top_z_distance": "0.1",
    },
    "0.4": {
        "compatible_printers": ["Bambu Lab H2S 0.4 nozzle"],
        "initial_layer_speed": ["35", "35"],
        "inner_wall_speed": ["150", "180"],
        "outer_wall_speed": ["100", "130"],
        "print_extruder_id": ["1", "1"],
        "print_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "sparse_infill_speed": ["200", "250"],
        "top_surface_speed": ["100", "130"],
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "enable_support": "1",
        "support_top_z_distance": "0.2",
    },
    "0.6": {
        "compatible_printers": ["Bambu Lab H2S 0.6 nozzle"],
        "initial_layer_speed": ["35", "35"],
        "inner_wall_speed": ["150", "180"],
        "outer_wall_speed": ["100", "130"],
        "print_extruder_id": ["1", "1"],
        "print_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "sparse_infill_speed": ["200", "250"],
        "top_surface_speed": ["100", "130"],
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "enable_support": "1",
        "support_top_z_distance": "0.2",
    },
    "0.8": {
        "compatible_printers": ["Bambu Lab H2S 0.8 nozzle"],
        "initial_layer_speed": ["35", "35"],
        "inner_wall_speed": ["150", "180"],
        "outer_wall_speed": ["100", "130"],
        "print_extruder_id": ["1", "1"],
        "print_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "sparse_infill_speed": ["200", "250"],
        "top_surface_speed": ["100", "130"],
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "wall_loops": "4",
        "enable_support": "1",
        "support_top_z_distance": "0.2",
    },
}


def gen_setting_id(prefix="PFUS"):
    return f"{prefix}{random.randbytes(6).hex()}"


def gen_info(setting_id, base_id="", user_id="2189385007"):
    ts = str(int(time.time()))
    lines = [
        "sync_info = ",
        f"user_id = {user_id}",
        f"setting_id = {setting_id}",
        f"base_id = {base_id}",
        f"updated_time = {ts}",
    ]
    return "\n".join(lines) + "\n"


def write_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.write("\n")


def write_info(path, content):
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(content)


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    deploy_dir = os.path.join(os.path.dirname(os.path.dirname(output_dir)), "DeployPack")

    base_setting_ids = {}

    # Generate base filament profiles (one per nozzle)
    for nozzle in NOZZLE_SIZES:
        overrides = OVERRIDES_02 if nozzle == "0.2" else BASE_OVERRIDES
        profile = dict(overrides)
        name = f"my-{BRAND} {MATERIAL} @Bambu Lab H2S {nozzle} nozzle"
        profile["name"] = name
        profile["filament_settings_id"] = [name]
        profile["compatible_printers"] = [NOZZLE_PRINTERS[nozzle]]
        profile["inherits"] = INHERITS_MAP[nozzle]

        json_path = os.path.join(output_dir, f"{name}.json")
        write_json(json_path, profile)

        sid = gen_setting_id("PFUS")
        base_setting_ids[nozzle] = sid
        info_path = os.path.join(output_dir, f"{name}.info")
        write_info(info_path, gen_info(sid))

        print(f"  Created: {name}.json + .info")

    # Generate user presets (sparse, inherits from our base)
    for nozzle in NOZZLE_SIZES:
        base_name = f"my-{BRAND} {MATERIAL} @Bambu Lab H2S {nozzle} nozzle"
        preset = {
            "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
            "filament_flow_ratio": ["nil", "nil"],
            "filament_settings_id": [base_name],
            "filament_type": ["PETG"],
            "from": "User",
            "inherits": base_name,
            "name": base_name,
            "version": VERSION,
        }

        json_path = os.path.join(output_dir, f"{base_name}.preset.json")
        write_json(json_path, preset)

        sid = gen_setting_id("PFUS")
        info_path = os.path.join(output_dir, f"{base_name}.preset.info")
        write_info(info_path, gen_info(sid, base_id=base_setting_ids[nozzle], user_id="2189385007"))

        print(f"  Created: {base_name}.preset.json + .info")

    # Generate calibrated override
    cal_name = f"my-{BRAND} {MATERIAL} Calibrated"
    cal_profile = {
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio": ["0.98", "0.98"],
        "filament_settings_id": [cal_name],
        "filament_type": ["PETG"],
        "from": "User",
        "inherits": f"my-{BRAND} {MATERIAL} @Bambu Lab H2S 0.4 nozzle",
        "name": cal_name,
        "pressure_advance": ["0.02"],
        "version": VERSION,
    }
    json_path = os.path.join(output_dir, f"{cal_name}.json")
    write_json(json_path, cal_profile)

    sid = gen_setting_id("PFUS")
    info_path = os.path.join(output_dir, f"{cal_name}.info")
    write_info(info_path, gen_info(sid, base_id=base_setting_ids["0.4"], user_id="2189385007"))
    print(f"  Created: {cal_name}.json + .info")

    # Generate process presets
    for nozzle in NOZZLE_SIZES:
        layer = LAYER_HEIGHTS[nozzle]
        proc_name = f"my-{BRAND} {MATERIAL} {layer}mm @H2S {nozzle} nozzle"
        overrides = PROCESS_OVERRIDES[nozzle]

        process = {
            "from": "User",
            "inherits": PROCESS_INHERITS[nozzle],
            "name": proc_name,
            "print_settings_id": proc_name,
            "version": VERSION,
        }
        for k, v in overrides.items():
            process[k] = v

        json_path = os.path.join(output_dir, f"{proc_name}.json")
        write_json(json_path, process)

        sid = gen_setting_id("PPUS")
        info_path = os.path.join(output_dir, f"{proc_name}.info")
        write_info(info_path, gen_info(sid, base_id=PROCESS_BASE_IDS[nozzle], user_id="2189385007"))

        print(f"  Created: {proc_name}.json + .info")

    # Copy all to DeployPack
    print(f"\n  Copying to DeployPack: {deploy_dir}")
    os.makedirs(deploy_dir, exist_ok=True)
    for fname in os.listdir(output_dir):
        if fname.startswith("my-") and (fname.endswith(".json") or fname.endswith(".info")):
            src = os.path.join(output_dir, fname)
            dst = os.path.join(deploy_dir, fname)
            shutil.copy2(src, dst)
            print(f"    Copied: {fname}")

    print("\nDone! All SUNLU PETG (standard) profiles generated.")


if __name__ == "__main__":
    main()
