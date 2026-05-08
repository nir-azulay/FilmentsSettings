import json, os, time, copy

base_dir = os.path.dirname(os.path.abspath(__file__))
deploy_dir = os.path.join(os.path.dirname(os.path.dirname(base_dir)), "DeployPack")
ts = int(time.time())

FILAMENT_ID = "Pf2a8e6c3"
BRAND = "GolGeo"
MATERIAL = "Silk PLA"
PREFIX = f"my-{BRAND} {MATERIAL}"

# Based on Generic PLA Silk @BBL H2S system profile merged with fdm_filament_common,
# fdm_filament_pla, Generic PLA Silk @base, and fdm_filament_template_direct_dual.
# Key values from Bambu system: nozzle 220/220 (0.4-0.8), 240/240 (0.2),
# flow ratio 0.98, retraction 0.4mm, fan_max 100%, fan_min 100% (PLA),
# slow_down_layer_time 10, max_vol 7.5 (0.4-0.8), 1 (0.2)

common_settings = {
    "activate_air_filtration": ["0"],
    "additional_cooling_fan_speed": ["75"],
    "additional_fan_full_speed_layer": ["0"],
    "chamber_temperatures": ["0"],
    "circle_compensation_speed": ["200"],
    "close_additional_fan_first_x_layers": ["1"],
    "close_fan_the_first_x_layers": ["1"],
    "compatible_printers_condition": "",
    "compatible_prints": [],
    "compatible_prints_condition": "",
    "complete_print_exhaust_fan_speed": ["70"],
    "cool_plate_temp": ["35"],
    "cool_plate_temp_initial_layer": ["35"],
    "cooling_perimeter_transition_distance": ["10"],
    "cooling_slowdown_logic": ["uniform_cooling"],
    "counter_coef_1": ["0"],
    "counter_coef_2": ["0.008"],
    "counter_coef_3": ["-0.041"],
    "counter_limit_max": ["0.033"],
    "counter_limit_min": ["-0.035"],
    "default_filament_colour": [""],
    "diameter_limit": ["50"],
    "during_print_exhaust_fan_speed": ["70"],
    "enable_overhang_bridge_fan": ["1"],
    "enable_pressure_advance": ["1"],
    "eng_plate_temp": ["55"],
    "eng_plate_temp_initial_layer": ["55"],
    "fan_cooling_layer_time": ["100"],
    "fan_max_speed": ["100"],
    "fan_min_speed": ["100"],
    "filament_adaptive_volumetric_speed": ["0", "0"],
    "filament_adhesiveness_category": ["100"],
    "filament_bridge_speed": ["25", "25"],
    "filament_change_length": ["10"],
    "filament_change_length_nc": ["10"],
    "filament_cooling_before_tower": ["10", "10"],
    "filament_cost": ["16.99"],
    "filament_density": ["1.24"],
    "filament_deretraction_speed": ["35", "35"],
    "filament_dev_ams_drying_ams_limitations": ["1", "0"],
    "filament_dev_ams_drying_heat_distortion_temperature": ["45"],
    "filament_dev_ams_drying_temperature": ["45", "45", "45", "45"],
    "filament_dev_ams_drying_time": ["12", "12", "12", "12"],
    "filament_dev_chamber_drying_bed_temperature": ["70"],
    "filament_dev_chamber_drying_time": ["12"],
    "filament_dev_drying_cooling_temperature": ["45"],
    "filament_dev_drying_softening_temperature": ["50"],
    "filament_diameter": ["1.75"],
    "filament_enable_overhang_speed": ["1", "1"],
    "filament_end_gcode": ["; filament end gcode \n"],
    "filament_extruder_compatibility": ["0"],
    "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
    "filament_flow_ratio": ["0.98", "0.98"],
    "filament_flush_temp": ["0", "0"],
    "filament_flush_volumetric_speed": ["0", "0"],
    "filament_id": FILAMENT_ID,
    "filament_is_support": ["0"],
    "filament_long_retractions_when_cut": ["1", "1"],
    "filament_metal_stickiness": ["None"],
    "filament_minimal_purge_on_wipe_tower": ["15"],
    "filament_notes": f"{BRAND} {MATERIAL} 1.75mm - Shiny Gold Silk PLA.\\nDimensional Accuracy +/- 0.02mm. 1kg spool.\\nBased on Generic PLA Silk @BBL H2S system profile.\\nNozzle: 220-240C, Bed: 35-55C, Full cooling (100%).\\nRetraction: 0.4mm @ 35mm/s. Density=1.24 g/cm3, Tg=45C.\\nFlow ratio 0.98 for silk finish. Outer wall 40-60mm/s for best gloss.",
    "filament_overhang_1_4_speed": ["0", "0"],
    "filament_overhang_2_4_speed": ["50", "50"],
    "filament_overhang_3_4_speed": ["30", "30"],
    "filament_overhang_4_4_speed": ["10", "10"],
    "filament_overhang_totally_speed": ["10", "10"],
    "filament_pre_cooling_temperature": ["0", "0"],
    "filament_pre_cooling_temperature_nc": ["0", "0"],
    "filament_prime_volume": ["45"],
    "filament_prime_volume_nc": ["60"],
    "filament_printable": ["3"],
    "filament_ramming_travel_time": ["0", "0"],
    "filament_ramming_travel_time_nc": ["0", "0"],
    "filament_ramming_volumetric_speed": ["-1", "-1"],
    "filament_ramming_volumetric_speed_nc": ["-1", "-1"],
    "filament_retract_before_wipe": ["1%", "1%"],
    "filament_retract_length_nc": ["14", "14"],
    "filament_retract_restart_extra": ["0", "0"],
    "filament_retract_when_changing_layer": ["1", "1"],
    "filament_retraction_distances_when_cut": ["18", "18"],
    "filament_retraction_length": ["0.4", "0.4"],
    "filament_retraction_minimum_travel": ["2", "2"],
    "filament_retraction_speed": ["35", "35"],
    "filament_scarf_gap": ["15%"],
    "filament_scarf_height": ["10%"],
    "filament_scarf_length": ["10"],
    "filament_scarf_seam_type": ["none"],
    "filament_shrink": ["100%"],
    "filament_soluble": ["0"],
    "filament_start_gcode": ["; filament start gcode\n{if  (bed_temperature[current_extruder] >45)||(bed_temperature_initial_layer[current_extruder] >45)}M106 P3 S255\n{elsif(bed_temperature[current_extruder] >35)||(bed_temperature_initial_layer[current_extruder] >35)}M106 P3 S180\n{endif};Prevent PLA from jamming\n\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"],
    "filament_tower_interface_pre_extrusion_dist": ["10"],
    "filament_tower_interface_pre_extrusion_length": ["0"],
    "filament_tower_interface_print_temp": ["-1"],
    "filament_tower_interface_purge_volume": ["20"],
    "filament_tower_ironing_area": ["4"],
    "filament_type": ["PLA"],
    "filament_velocity_adaptation_factor": ["1"],
    "filament_vendor": [BRAND],
    "filament_wipe": ["1", "1"],
    "filament_wipe_distance": ["1", "1"],
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
    "hot_plate_temp": ["55"],
    "hot_plate_temp_initial_layer": ["55"],
    "impact_strength_z": ["10"],
    "inherits": "",
    "ironing_fan_speed": ["-1"],
    "long_retractions_when_ec": ["0", "0"],
    "no_slow_down_for_cooling_on_outwalls": ["0"],
    "nozzle_temperature_range_high": ["240"],
    "nozzle_temperature_range_low": ["190"],
    "overhang_fan_speed": ["100"],
    "overhang_fan_threshold": ["50%"],
    "overhang_threshold_participating_cooling": ["95%"],
    "override_process_overhang_speed": ["0", "0"],
    "pre_start_fan_time": ["0"],
    "pressure_advance": ["0.02"],
    "reduce_fan_stop_start_freq": ["1"],
    "required_nozzle_HRC": ["3"],
    "retraction_distances_when_ec": ["0", "0"],
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["10"],
    "slow_down_min_speed": ["20", "20"],
    "supertack_plate_temp": ["35"],
    "supertack_plate_temp_initial_layer": ["35"],
    "temperature_vitrification": ["45"],
    "textured_plate_temp": ["55"],
    "textured_plate_temp_initial_layer": ["55"],
    "version": "2.6.0.2",
    "volumetric_speed_coefficients": ["0 0 0 0 0 0", "0 0 0 0 0 0"]
}

# Per-nozzle overrides from Bambu system profiles
nozzle_overrides = {
    "0.2": {
        "compatible_printers": ["Bambu Lab H2S 0.2 nozzle"],
        "filament_max_volumetric_speed": ["1", "1"],
        "filament_flush_volumetric_speed": ["3", "3"],
        "nozzle_temperature": ["240", "240"],
        "nozzle_temperature_initial_layer": ["240", "240"],
    },
    "0.4": {
        "compatible_printers": ["Bambu Lab H2S 0.4 nozzle"],
        "filament_max_volumetric_speed": ["7.5", "7.5"],
        "nozzle_temperature": ["220", "220"],
        "nozzle_temperature_initial_layer": ["220", "220"],
    },
    "0.6": {
        "compatible_printers": ["Bambu Lab H2S 0.6 nozzle"],
        "filament_max_volumetric_speed": ["7.5", "7.5"],
        "nozzle_temperature": ["220", "220"],
        "nozzle_temperature_initial_layer": ["220", "220"],
    },
    "0.8": {
        "compatible_printers": ["Bambu Lab H2S 0.8 nozzle"],
        "filament_max_volumetric_speed": ["7.5", "7.5"],
        "nozzle_temperature": ["220", "220"],
        "nozzle_temperature_initial_layer": ["220", "220"],
    },
}

# Generate base filament profiles
base_info_ids = {}
info_counter = 0xb1c2d3e4f500

for nozzle, overrides in nozzle_overrides.items():
    profile = copy.deepcopy(common_settings)
    profile.update(overrides)
    
    profile_name = f"{PREFIX} @Bambu Lab H2S {nozzle} nozzle"
    profile["name"] = profile_name
    profile["filament_settings_id"] = [profile_name]
    
    # Write JSON
    json_path = os.path.join(base_dir, f"{profile_name}.json")
    with open(json_path, "w", encoding="ascii", newline="") as f:
        json.dump(profile, f, indent=4, sort_keys=True)
        f.write("\n")
    
    # Write .info
    info_counter += 1
    setting_id = f"PFUS{info_counter:012x}"
    base_info_ids[nozzle] = setting_id
    
    info_path = os.path.join(base_dir, f"{profile_name}.info")
    with open(info_path, "w", encoding="ascii", newline="") as f:
        f.write(f"sync_info = \nuser_id = 2189385007\nsetting_id = {setting_id}\nbase_id = \nupdated_time = {ts}\n")

print(f"Created 4 base filament profiles")

# Generate Calibrated override
cal_name = f"{PREFIX} Calibrated"
cal_profile = {
    "filament_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
    "filament_flow_ratio": ["nil", "nil"],
    "filament_settings_id": [cal_name],
    "from": "User",
    "inherits": f"{PREFIX} @Bambu Lab H2S 0.4 nozzle",
    "name": cal_name,
    "version": "2.6.0.2"
}

json_path = os.path.join(base_dir, f"{cal_name}.json")
with open(json_path, "w", encoding="ascii", newline="") as f:
    json.dump(cal_profile, f, indent=4, sort_keys=True)
    f.write("\n")

info_counter += 1
cal_setting_id = f"PFUS{info_counter:012x}"
info_path = os.path.join(base_dir, f"{cal_name}.info")
with open(info_path, "w", encoding="ascii", newline="") as f:
    f.write(f"sync_info = \nuser_id = 2189385007\nsetting_id = {cal_setting_id}\nbase_id = {base_info_ids['0.4']}\nupdated_time = {ts}\n")

print(f"Created Calibrated override")

# Generate process presets
process_configs = {
    "0.2": {"inherits": "0.10mm Standard @BBL H2S 0.2 nozzle", "layer": "0.10", "base_id": "GP152",
             "inner_wall": "80", "outer_wall": "50", "infill": "80", "support_z": "0.1"},
    "0.4": {"inherits": "0.20mm Standard @BBL H2S", "layer": "0.20", "base_id": "GP158",
             "inner_wall": "120", "outer_wall": "60", "infill": "150", "support_z": "0.2"},
    "0.6": {"inherits": "0.30mm Standard @BBL H2S 0.6 nozzle", "layer": "0.30", "base_id": "GP159",
             "inner_wall": "150", "outer_wall": "60", "infill": "180", "support_z": "0.2"},
    "0.8": {"inherits": "0.40mm Standard @BBL H2S 0.8 nozzle", "layer": "0.40", "base_id": "GP156",
             "inner_wall": "150", "outer_wall": "60", "infill": "180", "support_z": "0.2"},
}

proc_counter = 0xc2d3e4f5a600

for nozzle, cfg in process_configs.items():
    proc_name = f"my-{BRAND} {MATERIAL} {cfg['layer']}mm @H2S {nozzle} nozzle"
    
    proc_profile = {
        "bridge_speed": ["25", "25"],
        "enable_support": "1",
        "from": "User",
        "inherits": cfg["inherits"],
        "initial_layer_speed": ["30", "30"],
        "inner_wall_speed": [cfg["inner_wall"], cfg["inner_wall"]],
        "name": proc_name,
        "outer_wall_speed": [cfg["outer_wall"], cfg["outer_wall"]],
        "print_extruder_id": ["1", "1"],
        "print_extruder_variant": ["Direct Drive Standard", "Direct Drive High Flow"],
        "print_settings_id": proc_name,
        "sparse_infill_density": "20%",
        "sparse_infill_pattern": "gyroid",
        "sparse_infill_speed": [cfg["infill"], cfg["infill"]],
        "support_top_z_distance": cfg["support_z"],
        "version": "2.6.0.2",
        "wall_loops": "4"
    }
    
    json_path = os.path.join(base_dir, f"{proc_name}.json")
    with open(json_path, "w", encoding="ascii", newline="") as f:
        json.dump(proc_profile, f, indent=4, sort_keys=True)
        f.write("\n")
    
    proc_counter += 1
    proc_setting_id = f"PPUS{proc_counter:012x}"
    
    info_path = os.path.join(base_dir, f"{proc_name}.info")
    with open(info_path, "w", encoding="ascii", newline="") as f:
        f.write(f"sync_info = \nuser_id = 2189385007\nsetting_id = {proc_setting_id}\nbase_id = {cfg['base_id']}\nupdated_time = {ts}\n")

print(f"Created 4 process presets")
print(f"\nAll files generated in: {base_dir}")
print(f"Base info IDs: {base_info_ids}")
