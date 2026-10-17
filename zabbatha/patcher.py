"""
Universal Config Patcher Engine for Zabbatha
Handles Snapshot Backups, Safe INI parsing/injection, and Read-Only Protection.
"""

import os
import shutil
import ctypes
from typing import Dict, Any, Tuple, Optional
from .database import get_game_profile
from .hdd_savior import inject_hdd_savior_to_engine_ini
from .hunter import find_game_config_autonomously

FILE_ATTRIBUTE_READONLY = 0x01
FILE_ATTRIBUTE_NORMAL = 0x80

def set_file_readonly(path: str, readonly: bool = True):
    """
    Toggles Windows Read-Only attribute on a file.
    """
    if not os.path.exists(path):
        return
    try:
        if readonly:
            ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_READONLY)
        else:
            ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_NORMAL)
    except Exception:
        pass

def backup_file_if_needed(target_path: str) -> str:
    """
    Creates a safe .zabbatha_backup copy before any modification if not already present.
    """
    backup_path = target_path + ".zabbatha_backup"
    if os.path.exists(target_path) and not os.path.exists(backup_path):
        try:
            shutil.copy2(target_path, backup_path)
        except Exception:
            pass
    return backup_path

def restore_backup(config_dir: str) -> Tuple[bool, str]:
    """
    Restores the original game configuration from snapshot backups.
    """
    restored = 0
    try:
        for fname in os.listdir(config_dir):
            if fname.endswith(".zabbatha_backup"):
                orig_name = fname[:-16] # remove .zabbatha_backup
                orig_path = os.path.join(config_dir, orig_name)
                backup_path = os.path.join(config_dir, fname)

                # Remove read-only on original if set
                set_file_readonly(orig_path, False)
                shutil.copy2(backup_path, orig_path)
                restored += 1

        if restored > 0:
            return True, f"Successfully restored {restored} original config files."
        return False, "No backup snapshot found to restore."
    except Exception as ex:
        return False, f"Failed restoring backup: {str(ex)}"

def resolve_game_config_dir(
    game_id: str,
    custom_config_dir: Optional[str] = None,
    game_name: str = "",
    install_dir: Optional[str] = None,
    exe_path: Optional[str] = None,
    engine_hint: str = "generic",
    app_id: Optional[int] = None
) -> str:
    """
    Intelligently finds or creates the config directory for any game using Autonomous Hunter.
    """
    if custom_config_dir and os.path.exists(custom_config_dir):
        return custom_config_dir

    db_profile = get_game_profile(game_id)
    paths = db_profile.get("config_paths", {})
    for k, p in paths.items():
        if os.path.exists(p):
            return p

    # Autonomous Config Hunter Engine
    res = find_game_config_autonomously(
        game_id=game_id,
        game_name=game_name or db_profile.get("name", game_id),
        install_dir=install_dir,
        exe_path=exe_path,
        engine_hint=engine_hint or db_profile.get("engine", "generic"),
        app_id=app_id or db_profile.get("app_id")
    )
    if res.config_dir and os.path.exists(res.config_dir):
        return res.config_dir

    if paths:
        return list(paths.values())[0]

    os.makedirs(res.config_dir, exist_ok=True)
    return res.config_dir

def restore_game_backup(
    game_id: str,
    custom_config_dir: Optional[str] = None,
    game_name: str = "",
    install_dir: Optional[str] = None,
    exe_path: Optional[str] = None,
    engine_hint: str = "generic",
    app_id: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Restores original configuration from backup for a specific game.
    """
    config_dir = resolve_game_config_dir(
        game_id,
        custom_config_dir=custom_config_dir,
        game_name=game_name,
        install_dir=install_dir,
        exe_path=exe_path,
        engine_hint=engine_hint,
        app_id=app_id
    )
    return restore_backup(config_dir)

def apply_game_profile(
    game_id: str,
    profile_id: str,
    enable_hdd_savior: bool = False,
    force_dx11: bool = False,
    custom_config_dir: Optional[str] = None,
    game_name: str = "",
    install_dir: Optional[str] = None,
    exe_path: Optional[str] = None,
    engine_hint: str = "generic",
    app_id: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Applies the chosen profile to the game's actual config files.
    """
    db_profile = get_game_profile(game_id)
    config_dir = resolve_game_config_dir(
        game_id,
        custom_config_dir=custom_config_dir,
        game_name=game_name,
        install_dir=install_dir,
        exe_path=exe_path,
        engine_hint=engine_hint,
        app_id=app_id
    )
    os.makedirs(config_dir, exist_ok=True)

    cfg_file = os.path.join(config_dir, db_profile.get("config_file_name", "GameUserSettings.ini"))
    engine_file = os.path.join(config_dir, db_profile.get("engine_ini_name", "Engine.ini"))

    # 1. Take Backup Snapshot
    backup_file_if_needed(cfg_file)
    backup_file_if_needed(engine_file)

    # 2. Unlock Read-Only on existing files before editing
    set_file_readonly(cfg_file, False)
    set_file_readonly(engine_file, False)

    # 3. Fetch Preset Data
    presets = db_profile.get("presets", {})
    preset_data = presets.get(profile_id, {})

    # --- Parse & Patch GameUserSettings.ini ---
    lines = []
    if os.path.exists(cfg_file):
        with open(cfg_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

    sections: Dict[str, Dict[str, str]] = {}
    current_sec = ""
    header_order = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_sec = stripped
            if current_sec not in sections:
                sections[current_sec] = {}
                header_order.append(current_sec)
        elif "=" in stripped and not stripped.startswith(";"):
            k, v = stripped.split("=", 1)
            if current_sec:
                sections[current_sec][k.strip()] = v.strip()

    # Apply Scalability
    scalability = preset_data.get("scalability", {})
    if scalability:
        sec_name = "[ScalabilityGroups]"
        if sec_name not in sections:
            sections[sec_name] = {}
            header_order.append(sec_name)
        for k, v in scalability.items():
            sections[sec_name][k] = v

    # Apply Embark Specific (ARC Raiders)
    embark_settings = preset_data.get("embark", {})
    if embark_settings:
        sec_name = "[/Script/EmbarkUserSettings.EmbarkGameUserSettings]"
        if sec_name not in sections:
            sections[sec_name] = {}
            header_order.append(sec_name)
        for k, v in embark_settings.items():
            sections[sec_name][k] = v

    # Apply Input Settings (Raw Mouse)
    input_settings = preset_data.get("input_settings", {})
    if input_settings:
        sec_name = "[/Script/Engine.InputSettings]"
        if sec_name not in sections:
            sections[sec_name] = {}
            header_order.append(sec_name)
        for k, v in input_settings.items():
            sections[sec_name][k] = v

    # Apply DX11 Force Toggle
    if force_dx11:
        sec_name = "[D3DRHIPreference]"
        if sec_name not in sections:
            sections[sec_name] = {}
            header_order.append(sec_name)
        sections[sec_name]["bUseD3D12InGame"] = "False"
    elif "D3DRHIPreference" in sections and not force_dx11:
        # Default back to True if not forced
        sections["[D3DRHIPreference]"]["bUseD3D12InGame"] = "True"

    # Write patched GameUserSettings.ini
    out_lines = []
    for sec in header_order:
        out_lines.append(f"{sec}\n")
        for k, v in sections[sec].items():
            out_lines.append(f"{k}={v}\n")
        out_lines.append("\n")

    with open(cfg_file, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

    # --- Apply Engine.ini CVars ---
    engine_cvars = preset_data.get("engine_cvars", {})
    if engine_cvars:
        eng_lines = []
        if os.path.exists(engine_file):
            with open(engine_file, "r", encoding="utf-8", errors="ignore") as f:
                eng_lines = f.readlines()

        eng_sections: Dict[str, Dict[str, str]] = {}
        curr_e_sec = ""
        e_header_order = []

        for line in eng_lines:
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                curr_e_sec = s
                if curr_e_sec not in eng_sections:
                    eng_sections[curr_e_sec] = {}
                    e_header_order.append(curr_e_sec)
            elif "=" in s and not s.startswith(";"):
                k, v = s.split("=", 1)
                if curr_e_sec:
                    eng_sections[curr_e_sec][k.strip()] = v.strip()

        sys_sec = "[SystemSettings]"
        if sys_sec not in eng_sections:
            eng_sections[sys_sec] = {}
            e_header_order.append(sys_sec)

        for k, v in engine_cvars.items():
            eng_sections[sys_sec][k] = v

        e_out_lines = []
        for sec in e_header_order:
            e_out_lines.append(f"{sec}\n")
            for k, v in eng_sections[sec].items():
                e_out_lines.append(f"{k}={v}\n")
            e_out_lines.append("\n")

        with open(engine_file, "w", encoding="utf-8") as f:
            f.writelines(e_out_lines)

    # --- Apply HDD Savior If Enabled ---
    if enable_hdd_savior:
        inject_hdd_savior_to_engine_ini(engine_file)

    # 4. Lock with Read-Only Guard to protect from in-game reset
    set_file_readonly(cfg_file, True)
    set_file_readonly(engine_file, True)

    return True, f"Profile '{profile_id}' applied & locked with Read-Only Guard."
