"""
Steam Hub & GreenLuma Integration Engine for Zabbatha
Handles Steam Library Detection, AppID Generation, Family Sharing Fixes, and Optimized Launching.
"""

import os
import sys
import subprocess
import winreg
from typing import Dict, Any, List, Optional, Tuple

def get_steam_path() -> Optional[str]:
    """
    Finds the active Steam installation directory via Registry or common paths.
    """
    # 1. Try Windows Registry
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        if steam_path and os.path.exists(steam_path):
            return os.path.normpath(steam_path)
    except Exception:
        pass

    # 2. Check standard directory locations
    candidates = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Steam",
        r"D:\steam",
        r"D:\SteamLibrary",
        r"E:\steam",
        r"E:\SteamLibrary"
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "steam.exe")):
            return c
    return None

def get_steam_users(steam_path: Optional[str] = None) -> List[str]:
    """
    Returns detected Steam account user IDs from the userdata directory.
    """
    sp = steam_path or get_steam_path()
    if not sp:
        return []
    ud_path = os.path.join(sp, "userdata")
    if not os.path.exists(ud_path):
        return []
    try:
        return [d for d in os.listdir(ud_path) if os.path.isdir(os.path.join(ud_path, d)) and d.isdigit()]
    except Exception:
        return []

def generate_greenluma_applist(app_ids: List[int], target_dir: Optional[str] = None) -> Tuple[bool, str, int]:
    """
    Generates a numbered AppList directory (0.txt, 1.txt, ...) compatible with GreenLuma / Steam Unlockers.
    Fixes Steam Family Sharing lock issues by creating a clean continuous AppList sequence.
    """
    steam_path = get_steam_path()
    dest = target_dir
    if not dest:
        if steam_path:
            dest = os.path.join(steam_path, "AppList")
        else:
            dest = os.path.join(os.getcwd(), "AppList")

    try:
        os.makedirs(dest, exist_ok=True)
        # Clear existing numbered .txt files in AppList
        for f in os.listdir(dest):
            if f.endswith(".txt") and f[:-4].isdigit():
                try:
                    os.remove(os.path.join(dest, f))
                except Exception:
                    pass

        count = 0
        for i, aid in enumerate(app_ids):
            file_path = os.path.join(dest, f"{i}.txt")
            with open(file_path, "w", encoding="utf-8") as fp:
                fp.write(str(aid).strip())
            count += 1

        return True, dest, count
    except Exception as ex:
        return False, str(ex), 0

def launch_game_optimized(
    exe_path: str,
    launch_args: Optional[List[str]] = None,
    force_high_priority: bool = True
) -> Tuple[bool, str]:
    """
    Launches a game executable with priority and performance command-line flags.
    """
    if not os.path.exists(exe_path):
        return False, f"Executable not found: {exe_path}"

    cmd = [exe_path]
    if launch_args:
        cmd.extend(launch_args)

    try:
        creationflags = 0
        if force_high_priority and sys.platform == "win32":
            # HIGH_PRIORITY_CLASS = 0x00000080
            creationflags = 0x00000080

        proc = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(exe_path),
            creationflags=creationflags
        )
        return True, f"Game launched successfully (PID: {proc.pid})"
    except Exception as ex:
        return False, f"Failed to launch game: {str(ex)}"
