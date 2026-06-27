import json
import time
from pathlib import Path


DEPLOYPACK = Path(r"C:\GitHub\filments settings\DeployPack")
USER_FILAMENT = Path(r"C:\Users\Nir\AppData\Roaming\BambuStudio\user\2189385007\filament")

# Device-tab AMS assignment follows Bambu Studio's own user preset format:
# a minimal user preset inheriting directly from a system H2S filament profile,
# with the .info base_id set to that system profile's setting_id.
PRESETS = [
    ("SUNLU TPU 95A", "Bambu TPU 95A @BBL H2S", "GFSU01_04"),
    ("SUNLU PETG", "Bambu PETG Basic @BBL H2S", "GFSG00_10"),
    ("SUNLU PETG HS", "Bambu PETG HF @BBL H2S", "GFSG02_10"),
    ("SUNLU PA E-PA", "Bambu PA6-GF @BBL H2S", "GFSN08_10"),
    ("SUNLU PLA", "Bambu PLA Basic @BBL H2S", "GFSA00_05"),
    ("Inslogic ASA", "Bambu ASA @BBL H2S", "GFSB01_26"),
    ("Inslogic PETG Pro", "Bambu PETG Basic @BBL H2S", "GFSG00_10"),
    ("Inslogic TPU 95A", "Bambu TPU 95A @BBL H2S", "GFSU01_04"),
    ("Inslogic PLA Pro", "Bambu PLA Basic @BBL H2S", "GFSA00_05"),
    ("Inslogic Matte PLA", "Bambu PLA Matte @BBL H2S", "GFSA01_07"),
    ("Inslogic Silk PLA", "Bambu PLA Silk @BBL H2S", "GFSA05_08"),
    ("Inslogic Nebulux PLA", "Bambu PLA Galaxy @BBL H2S", "GFSA15_11"),
]


def read_setting_id(info_path: Path, fallback_name: str) -> str:
    if info_path.exists():
        for line in info_path.read_text(encoding="ascii", errors="ignore").splitlines():
            if line.startswith("setting_id = "):
                setting_id = line.split("=", 1)[1].strip()
                if setting_id:
                    return setting_id

    # Stable fallback if an info file was cleaned by Bambu Studio.
    import hashlib

    digest = hashlib.sha1(fallback_name.encode("utf-8")).hexdigest()[:12]
    return f"PFUS{digest}"


def write_ascii(path: Path, content: str) -> None:
    path.write_text(content, encoding="ascii", newline="\n")


def main() -> None:
    updated_time = str(int(time.time()))

    for name, inherits, base_id in PRESETS:
        profile_name = f"{name} @Bambu Lab H2S"
        preset = {
            "filament_extruder_variant": [
                "Direct Drive Standard",
                "Direct Drive High Flow",
            ],
            "filament_settings_id": [profile_name],
            "from": "User",
            "inherits": inherits,
            "name": profile_name,
            "version": "2.7.0.8",
        }

        deploy_json = DEPLOYPACK / f"{profile_name}.preset.json"
        user_json = USER_FILAMENT / f"{profile_name}.json"
        for path in (deploy_json, user_json):
            path.write_text(json.dumps(preset, indent=4) + "\n", encoding="utf-8")

        deploy_info = DEPLOYPACK / f"{profile_name}.preset.info"
        user_info = USER_FILAMENT / f"{profile_name}.info"
        setting_id = read_setting_id(deploy_info, profile_name)
        info = (
            "sync_info = \n"
            "user_id = 2189385007\n"
            f"setting_id = {setting_id}\n"
            f"base_id = {base_id}\n"
            f"updated_time = {updated_time}\n"
        )
        for path in (deploy_info, user_info):
            write_ascii(path, info)

        print(f"{profile_name} -> {inherits} ({base_id})")


if __name__ == "__main__":
    main()
