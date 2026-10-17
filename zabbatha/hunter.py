"""
Smart Autonomous Game Config Hunter Engine for Zabbatha (2026 Pro Edition)
Autonomously locates game configuration directories, ini files, xmls, and json configs
across Windows user profiles, app data, documents, saved games, and install roots.
"""

import os
import re
import fnmatch
from typing import Dict, Any, List, Optional, Tuple

COMMON_CONFIG_FILES = [
    "GameUserSettings.ini",
    "Engine.ini",
    "Scalability.ini",
    "Input.ini",
    "GraphicsConfig.xml",
    "settings.xml",
    "config.ini",
    "options.ini",
    "options.txt",
    "video.txt",
    "cs2_video.txt",
    "settings.json",
    "display.ini",
    "PROFSAVE_profile"
]

class ConfigHunterResult:
    def __init__(
        self,
        config_dir: str,
        primary_file: str,
        engine_type: str = "generic",
        confidence: int = 100,
        source: str = "auto_detected"
    ):
        self.config_dir = config_dir
        self.primary_file = primary_file
        self.engine_type = engine_type
        self.confidence = confidence # 0 to 100
        self.source = source

    @property
    def full_path(self) -> str:
        return os.path.join(self.config_dir, self.primary_file) if self.primary_file else self.config_dir

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_dir": self.config_dir,
            "primary_file": self.primary_file,
            "full_path": self.full_path,
            "engine_type": self.engine_type,
            "confidence": self.confidence,
            "source": self.source
        }

def normalize_name(name: str) -> List[str]:
    """Generates fuzzy variations of game names for directory hunting."""
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", name).lower()
    parts = clean.split()
    variations = {
        name.lower(),
        clean,
        clean.replace(" ", ""),
        clean.replace(" ", "_"),
        clean.replace(" ", "-"),
        "".join([p[:3] for p in parts]), # short acronym
    }
    for p in parts:
        if len(p) >= 3 and p not in ["game", "the", "edition", "remastered", "trial", "trials"]:
            variations.add(p)
    return [v for v in variations if v]

def find_game_config_autonomously(
    game_id: str,
    game_name: str,
    install_dir: Optional[str] = None,
    exe_path: Optional[str] = None,
    engine_hint: str = "generic",
    app_id: Optional[int] = None
) -> ConfigHunterResult:
    """
    Intelligently discovers the configuration file for ANY game on Windows.
    Hunts through Steam UserData, UE project signatures, LocalAppData, Roaming AppData, Documents, and Install Tree.
    """
    local_app = os.environ.get("LOCALAPPDATA", "")
    roaming_app = os.environ.get("APPDATA", "")
    user_prof = os.environ.get("USERPROFILE", "")

    # Resolve Steam AppID if known
    target_appid = app_id
    if not target_appid and "cs2" in game_id.lower():
        target_appid = 730
    elif not target_appid and "arc" in game_id.lower():
        target_appid = 1808500

    # --- STEP 0: Steam UserData Direct Hunter ---
    if target_appid:
        steam_roots = ["C:\\Program Files (x86)\\Steam", "C:\\Steam", "D:\\steam", "D:\\SteamLibrary", "E:\\steam", "E:\\SteamLibrary"]
        for sroot in steam_roots:
            ud_dir = os.path.join(sroot, "userdata")
            if os.path.exists(ud_dir):
                try:
                    for uid in os.listdir(ud_dir):
                        cfg_target = os.path.join(ud_dir, uid, str(target_appid), "local", "cfg")
                        if os.path.exists(cfg_target):
                            files = os.listdir(cfg_target)
                            primary = files[0] if files else "config.cfg"
                            for f in files:
                                if "video" in f.lower() or "config" in f.lower():
                                    primary = f
                                    break
                            return ConfigHunterResult(
                                config_dir=cfg_target,
                                primary_file=primary,
                                engine_type="source_2" if target_appid == 730 else engine_hint,
                                confidence=100,
                                source=f"Steam_UserData({target_appid})"
                            )
                except Exception:
                    pass

    # --- STEP 1: Unreal Engine Internal Project Signature Matching ---
    # In UE4/UE5 games, the install directory has a subdirectory containing 'Binaries' or 'Content'.
    # That subdirectory name (e.g. PioneerGame, OPP, Astro, Sifu) is the EXACT folder in %LOCALAPPDATA%
    if install_dir and os.path.exists(install_dir) and local_app:
        try:
            for item in os.listdir(install_dir):
                item_full = os.path.join(install_dir, item)
                if os.path.isdir(item_full):
                    # Check if it has Binaries/Win64 or Content
                    has_bin = os.path.exists(os.path.join(item_full, "Binaries"))
                    has_content = os.path.exists(os.path.join(item_full, "Content"))
                    if has_bin or has_content:
                        # Test if %LOCALAPPDATA%\<item>\Saved\Config exists!
                        target_base = os.path.join(local_app, item, "Saved", "Config")
                        if os.path.exists(target_base):
                            for sub in ["WindowsClient", "WindowsNoEditor", "Windows", "WinGDK"]:
                                sub_path = os.path.join(target_base, sub)
                                if os.path.exists(sub_path):
                                    gus = os.path.join(sub_path, "GameUserSettings.ini")
                                    return ConfigHunterResult(
                                        config_dir=sub_path,
                                        primary_file="GameUserSettings.ini" if os.path.exists(gus) else (os.listdir(sub_path)[0] if os.listdir(sub_path) else "GameUserSettings.ini"),
                                        engine_type="unreal_engine_5" if "5" in engine_hint else "unreal_engine_4",
                                        confidence=100,
                                        source=f"UE_Project_Signature({item})"
                                    )
        except Exception:
            pass

    # --- STEP 2: Multi-Root AppData & Documents Hunting ---
    search_roots = []
    if local_app:
        search_roots.append(("local_appdata", local_app))
    if roaming_app:
        search_roots.append(("roaming_appdata", roaming_app))
    if user_prof:
        docs = os.path.join(user_prof, "Documents")
        my_games = os.path.join(user_prof, "Documents", "My Games")
        saved_games = os.path.join(user_prof, "Saved Games")
        if os.path.exists(my_games):
            search_roots.append(("my_games", my_games))
        if os.path.exists(docs):
            search_roots.append(("documents", docs))
        if os.path.exists(saved_games):
            search_roots.append(("saved_games", saved_games))

    variations = set(normalize_name(game_name) + normalize_name(game_id))
    if exe_path:
        exe_base = os.path.splitext(os.path.basename(exe_path))[0]
        variations.update(normalize_name(exe_base))

    # Known Aliases
    if any(k in game_id.lower() or k in game_name.lower() for k in ["arc", "pioneer"]):
        variations.update(["pioneergame", "pioneer", "arcraiders", "arc raiders"])
    if any(k in game_id.lower() or k in game_name.lower() for k in ["outlast", "tot"]):
        variations.update(["opp", "theoutlasttrials", "outlasttrials"])
    if "astroneer" in game_name.lower():
        variations.update(["astro"])

    for root_tag, root_path in search_roots:
        if not os.path.exists(root_path):
            continue
        try:
            entries = os.listdir(root_path)
            for entry in entries:
                entry_low = entry.lower()
                for var in variations:
                    if var == entry_low or (len(var) >= 4 and var in entry_low):
                        cand_dir = os.path.join(root_path, entry)
                        if not os.path.isdir(cand_dir):
                            continue

                        # Check for Unreal Engine standard structure
                        ue_saved_config = os.path.join(cand_dir, "Saved", "Config")
                        if os.path.exists(ue_saved_config):
                            for sub in ["WindowsClient", "WindowsNoEditor", "Windows", "WinGDK"]:
                                sub_path = os.path.join(ue_saved_config, sub)
                                if os.path.exists(sub_path):
                                    gus = os.path.join(sub_path, "GameUserSettings.ini")
                                    return ConfigHunterResult(
                                        config_dir=sub_path,
                                        primary_file="GameUserSettings.ini" if os.path.exists(gus) else (os.listdir(sub_path)[0] if os.listdir(sub_path) else "GameUserSettings.ini"),
                                        engine_type="unreal_engine_5" if "5" in engine_hint else "unreal_engine_4",
                                        confidence=95,
                                        source=f"{root_tag}/UE_Saved_Config"
                                    )

                        # Check for direct config files in the candidate folder
                        for fname in COMMON_CONFIG_FILES:
                            fp = os.path.join(cand_dir, fname)
                            if os.path.exists(fp):
                                return ConfigHunterResult(
                                    config_dir=cand_dir,
                                    primary_file=fname,
                                    engine_type=engine_hint,
                                    confidence=90,
                                    source=f"{root_tag}/direct"
                                )

                        # Check 1 level deeper (e.g. Documents/My Games/GameName/settings.xml)
                        try:
                            for sub_item in os.listdir(cand_dir):
                                sub_full = os.path.join(cand_dir, sub_item)
                                if os.path.isdir(sub_full):
                                    for fname in COMMON_CONFIG_FILES:
                                        if os.path.exists(os.path.join(sub_full, fname)):
                                            return ConfigHunterResult(
                                                config_dir=sub_full,
                                                primary_file=fname,
                                                engine_type=engine_hint,
                                                confidence=85,
                                                source=f"{root_tag}/subfolder"
                                            )
                        except Exception:
                            pass
        except Exception:
            continue

    # --- STEP 3: Check inside the Install Directory Tree ---
    if install_dir and os.path.exists(install_dir):
        # Look for game/csgo/cfg or cfg/ or binaries/
        for root, dirs, files in os.walk(install_dir):
            depth = root[len(install_dir):].count(os.sep)
            if depth > 3:
                continue

            for fname in files:
                fname_low = fname.lower()
                if fname_low in [c.lower() for c in COMMON_CONFIG_FILES] or (fname_low.endswith(".ini") and "default" not in fname_low):
                    return ConfigHunterResult(
                        config_dir=root,
                        primary_file=fname,
                        engine_type="source_2" if "cs2" in fname_low else engine_hint,
                        confidence=80,
                        source="install_dir_tree"
                    )

    # --- STEP 4: Fallback Default for Unreal Engine games ---
    fallback_dir = os.path.join(local_app, game_id, "Saved", "Config", "WindowsClient")
    return ConfigHunterResult(
        config_dir=fallback_dir,
        primary_file="GameUserSettings.ini",
        engine_type=engine_hint or "generic",
        confidence=40,
        source="fallback_default"
    )

if __name__ == "__main__":
    test_games = [
        ("arc_raiders", "ARC Raiders", r"D:\SteamLibrary\steamapps\common\Arc Raiders"),
        ("outlast_trials", "The Outlast Trials", r"E:\steam\steamapps\common\The Outlast Trials"),
        ("astroneer", "ASTRONEER", r"E:\steam\steamapps\common\ASTRONEER"),
        ("cs2", "Counter-Strike 2", r"E:\steam\steamapps\common\Counter-Strike Global Offensive")
    ]
    for gid, name, path in test_games:
        res = find_game_config_autonomously(gid, name, path)
        print(f"[{name}] -> Found: {res.full_path} (Confidence: {res.confidence}%, Source: {res.source})")
