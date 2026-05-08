"""
Generate Inslogic PETG Pro filament profiles for Bambu Lab H2S.

TDS: Inslogic_PETG_Pro_TDS.pdf (12.02.2024)
- Density: 1.26 g/cm3
- Tg: 65.5C
- HDT (0.45MPa): 72C
- Melting Temp: 128C
- Nozzle Temp: 230-270C (speed dependent)
- Bed Temp: 60-70C
- Drying: 50C, 4h
- Max Speed: 600mm/s
- Fan: TDS says 100%, using Bambu PETG values (60/20%) to prevent stringing

Using Bambu PETG Basic @BBL H2S as baseline for fan/retraction/flow settings.
"""

import json
import os
import random
import time

REPO_ROOT = r"c:\GitHub\filments settings"
BRAND_DIR = os.path.join(REPO_ROOT, "Inslogic", "PETG-Pro")
DEPLOY_DIR = os.path.join(REPO_ROOT, "DeployPack")
BAMBU_FILAMENT_BASE = r"C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament\base"
BAMBU_FILAMENT_USER = r"C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament"
BAMBU_PROCESS = r"C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\process"

VERSION = "2.6.0.2"
FILAMENT_ID = "Pc7e4a28"  # Unique ID for this filament

# Nozzle configs
NOZZLES = {
    "0.2": {
        "compatible_printers": ["Bambu Lab H2S 0.2 nozzle"],
        "process_inherits": "0.10mm Standard @BBL H2S 0.2 nozzle",
        "process_layer": "0.10mm",
        "process_base_id": "GP152",
        "nozzle_temperature": ["250", "250"],
        "nozzle_temperature_initial_layer": ["250", "250"],
        "filament_max_volumetric_speed": ["1", "1"],
        "filament_retraction_length": ["0.8", "0.8"],
    },
    "0.4": {
        "compatible_printers": ["Bambu Lab H2S 0.4 nozzle"],
        "process_inherits": "0.20mm Standard @BBL H2S",
        "process_layer": "0.20mm",
        "process_base_id": "GP158",
        "nozzle_temperature": ["245", "250"],
        "nozzle_temperature_initial_layer": ["250", "255"],
        "filament_max_volumetric_speed": ["18", "21"],
        "filament_retraction_length": ["0.8", "0.8"],
    },
    "0.6": {
        "compatible_printers": ["Bambu Lab H2S 0.6 nozzle"],
        "process_inherits": "0.30mm Standard @BBL H2S 0.6 nozzle",
        "process_layer": "0.30mm",
        "process_base_id": "GP159",
        "nozzle_temperature": ["250", "255"],
        "nozzle_temperature_initial_layer": ["255", "260"],
        "filament_max_volumetric_speed": ["21", "28"],
        "filament_retraction_length": ["0.8", "0.8"],
    },
    "0.8": {
        "compatible_printers": ["Bambu Lab H2S 0.8 nozzle"],
        "process_inherits": "0.40mm Standard @BBL H2S 0.8 nozzle",
        "process_layer": "0.40mm",
        "process_base_id": "GP156",
        "nozzle_temperature": ["255", "260"],
        "nozzle_temperature_initial_layer": ["260", "265"],
        "filament_max_volumetric_speed": ["21", "28"],
        "filament_retraction_length": ["0.8", "0.8"],
    },
}


def gen_hex(n):
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


def gen_filament_base(nozzle):
    """Generate a full base filament profile for a given nozzle size."""
    cfg = NOZZLES[nozzle]
    name = f"my-Inslogic PETG Pro @Bambu Lab H2S {nozzle} nozzle"

    profile = {
        "activate_air_filtration": ["0"],
        "additional_cooling_fan_speed": ["0"],
        "additional_fan_full_speed_layer": ["0"],
        "chamber_temperatures": ["0"],
        "circle_compensation_speed": ["200"],
        "close_additional_fan_first_x_layers": ["3"],
        "close_fan_the_first_x_layers": ["3"],
        "compatible_printers": cfg["compatible_printers"],
        "compatible_printers_condition": "",
        "compatible_prints": [],
        "compatible_prints_condition": "",
        "complete_print_exhaust_fan_speed": ["30"],
        "cool_plate_temp": ["65"],
        "cool_plate_temp_initial_layer": ["65"],
        "cooling_perimeter_transition_distance": ["10"],
        "cooling_slowdown_logic": ["uniform_cooling"],
        "counter_coef_1": ["0"],
        "counter_coef_2": ["0.008"],
        "counter_coef_3": ["-0.041"],
        "counter_limit_max": ["0.033"],
        "counter_limit_min": ["-0.035"],
        "default_filament_colour": [""],
        "diameter_limit": ["50"],
        "during_print_exhaust_fan_speed": ["30"],
        "enable_overhang_bridge_fan": ["1"],
        "enable_pressure_advance": ["1"],
        "eng_plate_temp": ["70"],
        "eng_plate_temp_initial_layer": ["70"],
        "fan_cooling_layer_time": ["30"],
        "fan_max_speed": ["60"],
        "fan_min_speed": ["20"],
        "filament_adaptive_volumetric_speed": ["0", "0"],
        "filament_adhesiveness_category": ["300"],
        "filament_bridge_speed": ["25", "25"],
        "filament_change_length": ["4"],
        "filament_change_length_nc": ["4"],
        "filament_cooling_before_tower": ["10", "10"],
        "filament_cost": ["20"],
        "filament_density": ["1.26"],
        "filament_deretraction_speed": ["35", "40"],
        "filament_dev_ams_drying_ams_limitations": [""],
        "filament_dev_ams_drying_heat_distortion_temperature": ["72"],
        "filament_dev_ams_drying_temperature": ["50"],
        "filament_dev_ams_drying_time": ["0"],
        "filament_dev_chamber_drying_bed_temperature": ["0"],
        "filament_dev_chamber_drying_time": ["0"],
        "filament_dev_drying_cooling_temperature": ["0"],
        "filament_dev_drying_softening_temperature": ["0"],
        "filament_diameter": ["1.75"],
        "filament_enable_overhang_speed": ["1", "1"],
        "filament_end_gcode": ["; filament end gcode \n"],
        "filament_extruder_compatibility": ["0"],
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio": ["0.97", "0.98"],
        "filament_flush_temp": ["0", "0"],
        "filament_flush_volumetric_speed": ["0", "0"],
        "filament_id": FILAMENT_ID,
        "filament_is_support": ["0"],
        "filament_long_retractions_when_cut": ["nil", "nil"],
        "filament_max_volumetric_speed": cfg["filament_max_volumetric_speed"],
        "filament_metal_stickiness": ["None"],
        "filament_minimal_purge_on_wipe_tower": ["15"],
        "filament_notes": "Inslogic PETG Pro - High-Speed Matte PETG. Nozzle: 230-270C (speed dependent). Bed: 60-70C (Textured PEI recommended). Retraction: 0.8mm at 35-40mm/s. Fan: max 60%, min 20%, overhang 50% (Bambu PETG baseline). Drying: 50C 4h. Density: 1.26 g/cm3. Tg: 65.5C. HDT: 72C. Max speed: 600mm/s. TDS: https://cdn.shopify.com/s/files/1/0822/8611/7163/files/Inslogic_PETG_Pro_Filament_Technical_Data_Sheet_TDS.pdf",
        "filament_overhang_1_4_speed": ["0", "0"],
        "filament_overhang_2_4_speed": ["0", "0"],
        "filament_overhang_3_4_speed": ["0", "0"],
        "filament_overhang_4_4_speed": ["0", "0"],
        "filament_overhang_totally_speed": ["10", "10"],
        "filament_pre_cooling_temperature": ["0", "0"],
        "filament_pre_cooling_temperature_nc": ["215", "215"],
        "filament_prime_volume": ["30"],
        "filament_prime_volume_nc": ["30"],
        "filament_printable": ["3"],
        "filament_ramming_travel_time": ["0", "0"],
        "filament_ramming_travel_time_nc": ["1", "1"],
        "filament_ramming_volumetric_speed": ["-1", "-1"],
        "filament_ramming_volumetric_speed_nc": ["-1", "-1"],
        "filament_retract_before_wipe": ["nil", "nil"],
        "filament_retract_length_nc": ["18", "18"],
        "filament_retract_restart_extra": ["nil", "nil"],
        "filament_retract_when_changing_layer": ["nil", "nil"],
        "filament_retraction_distances_when_cut": ["10", "10"],
        "filament_retraction_length": cfg["filament_retraction_length"],
        "filament_retraction_minimum_travel": ["nil", "nil"],
        "filament_retraction_speed": ["35", "40"],
        "filament_scarf_gap": ["0%"],
        "filament_scarf_height": ["10%"],
        "filament_scarf_length": ["10"],
        "filament_scarf_seam_type": ["none"],
        "filament_settings_id": [name],
        "filament_shrink": ["100%"],
        "filament_soluble": ["0"],
        "filament_start_gcode": [
            "; filament start gcode\n{if (bed_temperature[current_extruder] >80)||(bed_temperature_initial_layer[current_extruder] >80)}M106 P3 S255\n{elsif (bed_temperature[current_extruder] >60)||(bed_temperature_initial_layer[current_extruder] >60)}M106 P3 S180\n{endif}\n\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"
        ],
        "filament_tower_interface_pre_extrusion_dist": ["10"],
        "filament_tower_interface_pre_extrusion_length": ["0"],
        "filament_tower_interface_print_temp": ["-1"],
        "filament_tower_interface_purge_volume": ["20"],
        "filament_tower_ironing_area": ["4"],
        "filament_type": ["PETG"],
        "filament_velocity_adaptation_factor": ["1"],
        "filament_vendor": ["Inslogic"],
        "filament_wipe": ["1", "1"],
        "filament_wipe_distance": ["2", "2"],
        "filament_z_hop": ["nil", "nil"],
        "filament_z_hop_types": ["Spiral Lift", "Spiral Lift"],
        "first_x_layer_fan_speed": ["0"],
        "first_x_layer_part_fan_speed": ["0"],
        "from": "User",
        "full_fan_speed_layer": ["0"],
        "hole_coef_1": ["0"],
        "hole_coef_2": ["-0.008"],
        "hole_coef_3": ["0.23415"],
        "hole_limit_max": ["0.22"],
        "hole_limit_min": ["0.088"],
        "hot_plate_temp": ["70"],
        "hot_plate_temp_initial_layer": ["70"],
        "impact_strength_z": ["10"],
        "inherits": "",
        "ironing_fan_speed": ["-1"],
        "long_retractions_when_ec": ["1", "1"],
        "name": name,
        "no_slow_down_for_cooling_on_outwalls": ["0"],
        "nozzle_temperature": cfg["nozzle_temperature"],
        "nozzle_temperature_initial_layer": cfg["nozzle_temperature_initial_layer"],
        "nozzle_temperature_range_high": ["270"],
        "nozzle_temperature_range_low": ["230"],
        "overhang_fan_speed": ["50"],
        "overhang_fan_threshold": ["10%"],
        "overhang_threshold_participating_cooling": ["95%"],
        "override_process_overhang_speed": ["0", "0"],
        "pre_start_fan_time": ["2"],
        "pressure_advance": ["0.02"],
        "reduce_fan_stop_start_freq": ["1"],
        "required_nozzle_HRC": ["3"],
        "retraction_distances_when_ec": ["10", "10"],
        "slow_down_for_layer_cooling": ["1"],
        "slow_down_layer_time": ["12"],
        "slow_down_min_speed": ["20", "20"],
        "supertack_plate_temp": ["70"],
        "supertack_plate_temp_initial_layer": ["70"],
        "temperature_vitrification": ["65"],
        "textured_plate_temp": ["70"],
        "textured_plate_temp_initial_layer": ["70"],
        "version": VERSION,
        "volumetric_speed_coefficients": ["0 0 0 0 0 0", "0 0 0 0 0 0"],
    }
    return profile


def gen_filament_user_preset(nozzle):
    """Generate a sparse user preset that inherits from the base."""
    base_name = f"my-Inslogic PETG Pro @Bambu Lab H2S {nozzle} nozzle"
    return {
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio": ["nil", "nil"],
        "filament_settings_id": [base_name],
        "from": "User",
        "inherits": base_name,
        "name": base_name,
        "version": VERSION,
    }


def gen_calibrated():
    """Generate the Calibrated override preset."""
    return {
        "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "filament_flow_ratio": ["nil", "nil"],
        "filament_settings_id": ["my-Inslogic PETG Pro Calibrated"],
        "from": "User",
        "inherits": "my-Inslogic PETG Pro @Bambu Lab H2S 0.4 nozzle",
        "name": "my-Inslogic PETG Pro Calibrated",
        "version": VERSION,
    }


def gen_process_preset(nozzle):
    """Generate a process preset using Bambu baseline + PETG-appropriate overrides."""
    cfg = NOZZLES[nozzle]
    name = f"my-Inslogic PETG Pro {cfg['process_layer']} @H2S {nozzle} nozzle"

    # PETG Pro is high-speed capable - use speeds similar to SUNLU PETG HS
    speed_overrides = {
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
        },
        "0.6": {
            "initial_layer_speed": ["40", "45"],
            "inner_wall_speed": ["250", "300"],
            "outer_wall_speed": ["120", "150"],
            "sparse_infill_speed": ["300", "350"],
        },
        "0.8": {
            "initial_layer_speed": ["40", "45"],
            "inner_wall_speed": ["250", "300"],
            "outer_wall_speed": ["120", "150"],
            "sparse_infill_speed": ["300", "350"],
        },
    }

    support_z = {"0.2": "0.1", "0.4": "0.2", "0.6": "0.3", "0.8": "0.4"}

    preset = {}
    speeds = speed_overrides[nozzle]
    for key in sorted(speeds.keys()):
        preset[key] = speeds[key]

    preset["enable_support"] = "1"
    preset["from"] = "User"
    preset["inherits"] = cfg["process_inherits"]
    preset["name"] = name
    preset["print_extruder_id"] = ["1", "1"]
    preset["print_extruder_variant"] = ["Direct Drive Standard", "Direct Drive High Flow"]
    preset["print_settings_id"] = name
    preset["sparse_infill_density"] = "20%"
    preset["sparse_infill_pattern"] = "gyroid"
    preset["support_top_z_distance"] = support_z[nozzle]
    preset["version"] = VERSION
    preset["wall_loops"] = "4"

    return preset


def write_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.write("\n")


def write_info(content, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="ascii", newline="\n") as f:
        f.write(content)


def gen_info(prefix, base_id=""):
    setting_id = f"{prefix}{gen_hex(12)}"
    ts = int(time.time())
    return setting_id, f"sync_info = \nuser_id = 2189385007\nsetting_id = {setting_id}\nbase_id = {base_id}\nupdated_time = {ts}\n"


def main():
    print("Generating Inslogic PETG Pro profiles...")
    print()

    # 1. Base filament profiles
    print("=== Base Filament Profiles ===")
    base_setting_ids = {}
    for nozzle in ["0.2", "0.4", "0.6", "0.8"]:
        profile = gen_filament_base(nozzle)
        name = profile["name"]
        setting_id, info_content = gen_info("PFUS")
        base_setting_ids[nozzle] = setting_id

        for dest_dir in [BAMBU_FILAMENT_BASE, BRAND_DIR, DEPLOY_DIR]:
            write_json(profile, os.path.join(dest_dir, f"{name}.json"))
            write_info(info_content, os.path.join(dest_dir, f"{name}.info"))

        print(f"  {name}")

    # 2. Filament user presets
    print("\n=== Filament User Presets ===")
    for nozzle in ["0.2", "0.4", "0.6", "0.8"]:
        preset = gen_filament_user_preset(nozzle)
        name = preset["name"]
        _, info_content = gen_info("PFUS", base_setting_ids[nozzle])

        # User presets go to filament dir (not base) and DeployPack as .preset.*
        write_json(preset, os.path.join(BAMBU_FILAMENT_USER, f"{name}.json"))
        write_info(info_content, os.path.join(BAMBU_FILAMENT_USER, f"{name}.info"))

        # DeployPack uses .preset.json/.preset.info naming
        write_json(preset, os.path.join(DEPLOY_DIR, f"{name}.preset.json"))
        write_info(info_content, os.path.join(DEPLOY_DIR, f"{name}.preset.info"))

        # Brand dir
        write_json(preset, os.path.join(BRAND_DIR, f"{name}.preset.json"))
        write_info(info_content, os.path.join(BRAND_DIR, f"{name}.preset.info"))

        print(f"  {name}")

    # 3. Calibrated override
    print("\n=== Calibrated Override ===")
    calibrated = gen_calibrated()
    cal_name = calibrated["name"]
    _, cal_info = gen_info("PFUS", base_setting_ids["0.4"])

    write_json(calibrated, os.path.join(BAMBU_FILAMENT_USER, f"{cal_name}.json"))
    write_info(cal_info, os.path.join(BAMBU_FILAMENT_USER, f"{cal_name}.info"))
    write_json(calibrated, os.path.join(DEPLOY_DIR, f"{cal_name}.json"))
    write_info(cal_info, os.path.join(DEPLOY_DIR, f"{cal_name}.info"))
    write_json(calibrated, os.path.join(BRAND_DIR, f"{cal_name}.json"))
    write_info(cal_info, os.path.join(BRAND_DIR, f"{cal_name}.info"))
    print(f"  {cal_name}")

    # 4. Process presets
    print("\n=== Process Presets ===")
    for nozzle in ["0.2", "0.4", "0.6", "0.8"]:
        cfg = NOZZLES[nozzle]
        preset = gen_process_preset(nozzle)
        name = preset["name"]
        _, info_content = gen_info("PPUS", cfg["process_base_id"])

        for dest_dir in [BAMBU_PROCESS, BRAND_DIR, DEPLOY_DIR]:
            write_json(preset, os.path.join(dest_dir, f"{name}.json"))
            write_info(info_content, os.path.join(dest_dir, f"{name}.info"))

        print(f"  {name}")

    print("\nDone! All profiles generated.")


if __name__ == "__main__":
    main()
