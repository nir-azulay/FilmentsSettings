#!/usr/bin/env python3
"""Generate YS Filament ABS profiles for Bambu Lab H2S (all nozzle sizes)."""

import json
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
TIMESTAMP = 1749279600

FILAMENT_START_GCODE = (
    "; filament start gcode\n"
    "{if (bed_temperature[current_extruder] >80)||(bed_temperature_initial_layer[current_extruder] >80)}"
    "M106 P3 S255\n"
    "{elsif (bed_temperature[current_extruder] >60)||(bed_temperature_initial_layer[current_extruder] >60)}"
    "M106 P3 S180\n"
    "{endif}\n"
    "\n"
    "{if activate_air_filtration[current_extruder] && support_air_filtration}\n"
    "M106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n"
    "{endif}"
)

NOZZLES = ["0.2", "0.4", "0.6", "0.8"]

BASE_SETTING_IDS = {
    "0.2": "PFUSa3e7f1b2c4d6",
    "0.4": "PFUS8b9c0d1e2f3a",
    "0.6": "PFUS5d6c7b8a9e0f",
    "0.8": "PFUSf4e3d2c1b0a9",
}

PRESET_SETTING_IDS = {
    "0.2": "PFUS1a2b3c4d5e6f",
    "0.4": "PFUS7e8f9a0b1c2d",
    "0.6": "PFUS3d4e5f6a7b8c",
    "0.8": "PFUSd9e0f1a2b3c4",
}

CALIBRATED_SETTING_ID = "PFUS6a7b8c9d0e1f"

PROCESS_SETTING_IDS = {
    "0.2": "PPUSab12cd34ef56",
    "0.4": "PPUS78ef90ab12cd",
    "0.6": "PPUSde34f567ab89",
    "0.8": "PPUS01cd23ef45ab",
}

PROCESS_CONFIG = {
    "0.2": {
        "layer": "0.10",
        "inherits": "0.10mm Standard @BBL H2S 0.2 nozzle",
        "base_id": "GP152",
        "support_top_z_distance": "0.1",
    },
    "0.4": {
        "layer": "0.20",
        "inherits": "0.20mm Standard @BBL H2S",
        "base_id": "GP158",
        "support_top_z_distance": "0.2",
    },
    "0.6": {
        "layer": "0.30",
        "inherits": "0.30mm Standard @BBL H2S 0.6 nozzle",
        "base_id": "GP159",
        "support_top_z_distance": "0.2",
    },
    "0.8": {
        "layer": "0.40",
        "inherits": "0.40mm Standard @BBL H2S 0.8 nozzle",
        "base_id": "GP156",
        "support_top_z_distance": "0.2",
    },
}


def write_json(path, data):
    with open(path, "w", encoding="ascii", newline="\n") as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.write("\n")


def write_info(path, content):
    with open(path, "w", encoding="ascii", newline="") as f:
        f.write(content)


def build_base_profile(nozzle):
    name = f"my-YS Filament ABS @Bambu Lab H2S {nozzle} nozzle"

    is_02 = nozzle == "0.2"

    profile = {
        "activate_air_filtration": ["1"],
        "additional_cooling_fan_speed": ["0"],
        "additional_fan_full_speed_layer": ["0"],
        "chamber_temperatures": ["60"],
        "circle_compensation_speed": ["200"],
        "close_additional_fan_first_x_layers": ["3"],
        "close_fan_the_first_x_layers": ["3"],
        "compatible_printers": [f"Bambu Lab H2S {nozzle} nozzle"],
        "compatible_printers_condition": "",
        "compatible_prints": [],
        "compatible_prints_condition": "",
        "complete_print_exhaust_fan_speed": ["30"],
        "cool_plate_temp": ["0"],
        "cool_plate_temp_initial_layer": ["0"],
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
        "eng_plate_temp": ["90"],
        "eng_plate_temp_initial_layer": ["90"],
        "fan_cooling_layer_time": ["30"],
        "fan_max_speed": ["60"] if is_02 else ["80"],
        "fan_min_speed": ["40"] if is_02 else ["10"],
        "filament_adaptive_volumetric_speed": ["0", "0"],
        "filament_adhesiveness_category": ["300"],
        "filament_bridge_speed": ["25", "25"],
        "filament_change_length": ["4"],
        "filament_change_length_nc": ["4"],
        "filament_cooling_before_tower": ["10", "10"],
        "filament_cost": ["20"],
        "filament_density": ["1.05"],
        "filament_deretraction_speed": ["35", "35"],
        "filament_dev_ams_drying_ams_limitations": ["1", "0"],
        "filament_dev_ams_drying_heat_distortion_temperature": ["83"],
        "filament_dev_ams_drying_temperature": ["65", "65", "55", "55"],
        "filament_dev_ams_drying_time": ["12", "12", "12", "12"],
        "filament_dev_chamber_drying_bed_temperature": ["80"],
        "filament_dev_chamber_drying_time": ["12"],
        "filament_dev_drying_cooling_temperature": ["55"],
        "filament_dev_drying_softening_temperature": ["100"],
        "filament_diameter": ["1.75"],
        "filament_enable_overhang_speed": ["0", "0"],
        "filament_end_gcode": ["; filament end gcode \n"],
        "filament_extruder_compatibility": ["0"],
        "filament_extruder_variant": [
            "Direct Drive Standard",
            "Direct Drive High Flow",
        ],
        "filament_flow_ratio": ["0.95"],
        "filament_flush_temp": ["0", "0"],
        "filament_flush_volumetric_speed": ["0", "0"],
        "filament_id": "P6d8a4f2e",
        "filament_is_support": ["0"],
        "filament_long_retractions_when_cut": ["nil", "nil"],
        "filament_max_volumetric_speed": (
            ["2", "2"] if is_02 else ["15", "15"]
        ),
        "filament_metal_stickiness": ["None"],
        "filament_minimal_purge_on_wipe_tower": ["15"],
        "filament_notes": (
            "YS Filament ABS. Nozzle: 270\u00b0C (Bambu system, TDS 220-250\u00b0C). "
            "Bed: 90\u00b0C. Chamber: 60\u00b0C. "
            + (
                "Fan: max 60%, min 40% (0.2mm nozzle). "
                if is_02
                else "Fan: max 80%, min 10%. "
            )
            + "Density: 1.05 g/cm\u00b3. Vicat: 100\u00b0C. HDT: 83\u00b0C. "
            "Tensile: 47 MPa. Shrinkage: 0.4-0.7%. "
            "Air filtration enabled."
        ),
        "filament_overhang_1_4_speed": ["0", "0"],
        "filament_overhang_2_4_speed": ["50", "50"],
        "filament_overhang_3_4_speed": ["30", "30"],
        "filament_overhang_4_4_speed": ["10", "10"],
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
        "filament_retraction_length": (
            ["0.8", "0.8"] if is_02 else ["0.4", "0.4"]
        ),
        "filament_retraction_minimum_travel": ["nil", "nil"],
        "filament_retraction_speed": ["35", "35"],
        "filament_scarf_gap": ["0%"],
        "filament_scarf_height": ["10%"],
        "filament_scarf_length": ["10"],
        "filament_scarf_seam_type": ["none"],
        "filament_settings_id": [name],
        "filament_shrink": ["100%"],
        "filament_soluble": ["0"],
        "filament_start_gcode": [FILAMENT_START_GCODE],
        "filament_tower_interface_pre_extrusion_dist": ["10"],
        "filament_tower_interface_pre_extrusion_length": ["0"],
        "filament_tower_interface_print_temp": ["-1"],
        "filament_tower_interface_purge_volume": ["20"],
        "filament_tower_ironing_area": ["4"],
        "filament_type": ["ABS"],
        "filament_velocity_adaptation_factor": ["1"],
        "filament_vendor": ["YS Filament"],
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
        "hot_plate_temp": ["90"],
        "hot_plate_temp_initial_layer": ["90"],
        "impact_strength_z": ["10"],
        "inherits": "",
        "ironing_fan_speed": ["-1"],
        "long_retractions_when_ec": ["1", "1"],
        "name": name,
        "no_slow_down_for_cooling_on_outwalls": ["0"],
        "nozzle_temperature": ["270", "270"],
        "nozzle_temperature_initial_layer": ["260", "260"],
        "nozzle_temperature_range_high": ["290"],
        "nozzle_temperature_range_low": ["220"],
        "overhang_fan_speed": ["80"],
        "overhang_fan_threshold": ["10%"],
        "overhang_threshold_participating_cooling": ["95%"],
        "override_process_overhang_speed": ["0", "0"],
        "pre_start_fan_time": ["2"],
        "pressure_advance": ["0.02"],
        "reduce_fan_stop_start_freq": ["1"],
        "required_nozzle_HRC": ["3"],
        "retraction_distances_when_ec": ["10", "10"],
        "slow_down_for_layer_cooling": ["1"],
        "slow_down_layer_time": ["8"],
        "slow_down_min_speed": ["20", "20"],
        "supertack_plate_temp": ["70"],
        "supertack_plate_temp_initial_layer": ["70"],
        "temperature_vitrification": ["100"],
        "textured_plate_temp": ["90"],
        "textured_plate_temp_initial_layer": ["90"],
        "version": "2.6.0.2",
        "volumetric_speed_coefficients": [
            "0 0 0 0 0 0",
            "0 0 0 0 0 0",
        ],
    }
    return profile


def build_user_preset(nozzle):
    name = f"my-YS Filament ABS @Bambu Lab H2S {nozzle} nozzle"
    return {
        "filament_extruder_variant": [
            "Direct Drive Standard",
            "Direct Drive High Flow",
        ],
        "filament_flow_ratio": ["nil", "nil"],
        "filament_settings_id": [name],
        "from": "User",
        "inherits": name,
        "name": name,
        "version": "2.6.0.2",
    }


def build_calibrated():
    return {
        "filament_extruder_variant": [
            "Direct Drive Standard",
            "Direct Drive High Flow",
        ],
        "filament_flow_ratio": ["nil", "nil"],
        "filament_settings_id": ["my-YS Filament ABS Calibrated"],
        "from": "User",
        "inherits": "my-YS Filament ABS @Bambu Lab H2S 0.4 nozzle",
        "name": "my-YS Filament ABS Calibrated",
        "version": "2.6.0.2",
    }


def build_process_preset(nozzle):
    cfg = PROCESS_CONFIG[nozzle]
    name = f"my-YS Filament ABS {cfg['layer']}mm @H2S {nozzle} nozzle"
    return {
        "brim_type": "outer_and_inner",
        "brim_width": "5",
        "compatible_filaments": [],
        "compatible_filaments_condition": "",
        "compatible_printers": [],
        "compatible_printers_condition": "",
        "enable_support": "1",
        "from": "User",
        "inherits": cfg["inherits"],
        "initial_layer_speed": "30",
        "name": name,
        "print_settings_id": name,
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "support_top_z_distance": cfg["support_top_z_distance"],
        "version": "2.6.0.2",
        "wall_loops": "4",
    }


def make_info(sync="", user_id="", setting_id="", base_id="", ts=TIMESTAMP):
    return (
        f"sync_info = {sync}\n"
        f"user_id = {user_id}\n"
        f"setting_id = {setting_id}\n"
        f"base_id = {base_id}\n"
        f"updated_time = {ts}\n"
    )


def main():
    created = []

    for nozzle in NOZZLES:
        base_name = f"my-YS Filament ABS @Bambu Lab H2S {nozzle} nozzle"

        # --- Base filament profile ---
        base_json_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")
        write_json(base_json_path, build_base_profile(nozzle))
        created.append(base_json_path)

        base_info_path = os.path.join(OUTPUT_DIR, f"{base_name}.info")
        write_info(
            base_info_path,
            make_info(setting_id=BASE_SETTING_IDS[nozzle]),
        )
        created.append(base_info_path)

        # --- User preset ---
        preset_json_path = os.path.join(OUTPUT_DIR, f"{base_name}.preset.json")
        write_json(preset_json_path, build_user_preset(nozzle))
        created.append(preset_json_path)

        preset_info_path = os.path.join(OUTPUT_DIR, f"{base_name}.preset.info")
        write_info(
            preset_info_path,
            make_info(
                user_id="2189385007",
                setting_id=PRESET_SETTING_IDS[nozzle],
                base_id=BASE_SETTING_IDS[nozzle],
            ),
        )
        created.append(preset_info_path)

        # --- Process preset ---
        cfg = PROCESS_CONFIG[nozzle]
        proc_name = f"my-YS Filament ABS {cfg['layer']}mm @H2S {nozzle} nozzle"
        proc_json_path = os.path.join(OUTPUT_DIR, f"{proc_name}.json")
        write_json(proc_json_path, build_process_preset(nozzle))
        created.append(proc_json_path)

        proc_info_path = os.path.join(OUTPUT_DIR, f"{proc_name}.info")
        write_info(
            proc_info_path,
            make_info(
                user_id="2189385007",
                setting_id=PROCESS_SETTING_IDS[nozzle],
                base_id=cfg["base_id"],
            ),
        )
        created.append(proc_info_path)

    # --- Calibrated override ---
    cal_json_path = os.path.join(OUTPUT_DIR, "my-YS Filament ABS Calibrated.json")
    write_json(cal_json_path, build_calibrated())
    created.append(cal_json_path)

    cal_info_path = os.path.join(OUTPUT_DIR, "my-YS Filament ABS Calibrated.info")
    write_info(
        cal_info_path,
        make_info(
            user_id="2189385007",
            setting_id=CALIBRATED_SETTING_ID,
            base_id=BASE_SETTING_IDS["0.4"],
        ),
    )
    created.append(cal_info_path)

    print(f"Created {len(created)} files:")
    for p in created:
        print(f"  {os.path.basename(p)}")


if __name__ == "__main__":
    main()
