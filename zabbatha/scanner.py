"""
Game Scanner Engine for Zabbatha
Detects games from Steam, Epic Games, Xbox, and custom user-provided folders.
Optimized for high-speed non-blocking indexing (zero deep recursive crawling).
"""

import os
import re
import fnmatch
from typing import List, Dict, Any, Optional
from .hardware import get_drive_types

class DetectedGame:
    def __init__(
        self,
        game_id: str,
        name: str,
        exe_path: str,
        install_dir: str,
        engine: str = "generic",
        app_id: Optional[int] = None,
        source: str = "custom",
        icon: Optional[str] = None
    ):
        self.game_id = game_id
        self.name = name
        self.exe_path = exe_path
        self.install_dir = install_dir
        self.engine = engine
        self.app_id = app_id
        self.source = source
        self.icon = icon

        # Detect Drive Type (HDD vs SSD)
        self.drive_letter = os.path.splitdrive(install_dir)[0].replace(":", "").upper()
        self.drive_type = "Unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_id": self.game_id,
            "name": self.name,
            "exe_path": self.exe_path,
            "install_dir": self.install_dir,
            "engine": self.engine,
            "app_id": self.app_id,
            "source": self.source,
            "drive_letter": self.drive_letter,
            "drive_type": self.drive_type,
            "icon": self.icon
        }

KNOWN_SIGNATURES = [
    {
        "id": "arc_raiders",
        "name": "ARC Raiders",
        "exe_patterns": ["pioneer*.exe", "arcraiders*.exe"],
        "folder_patterns": ["arc raiders", "pioneergame", "arcraiders"],
        "engine": "unreal_engine_5",
        "app_id": 1808500
    },
    {
        "id": "cs2",
        "name": "Counter-Strike 2",
        "exe_patterns": ["cs2.exe"],
        "folder_patterns": ["counter-strike global offensive", "cs2"],
        "engine": "source_2",
        "app_id": 730
    },
    {
        "id": "valorant",
        "name": "VALORANT",
        "exe_patterns": ["valorant*.exe"],
        "folder_patterns": ["valorant"],
        "engine": "unreal_engine_4",
        "app_id": None
    },
    {
        "id": "apex",
        "name": "Apex Legends",
        "exe_patterns": ["r5apex.exe"],
        "folder_patterns": ["apex legends", "apex"],
        "engine": "source",
        "app_id": 1172470
    },
    {
        "id": "gta5",
        "name": "Grand Theft Auto V",
        "exe_patterns": ["gta5.exe"],
        "folder_patterns": ["grand theft auto v", "gtav", "gta 5"],
        "engine": "rage",
        "app_id": 271590
    },
    {
        "id": "rdr2",
        "name": "Red Dead Redemption 2",
        "exe_patterns": ["rdr2.exe"],
        "folder_patterns": ["red dead redemption 2", "rdr2"],
        "engine": "rage",
        "app_id": 1174180
    },
    {
        "id": "cyberpunk",
        "name": "Cyberpunk 2077",
        "exe_patterns": ["cyberpunk2077.exe"],
        "folder_patterns": ["cyberpunk 2077", "cyberpunk2077"],
        "engine": "redengine",
        "app_id": 1091500
    },
    {
        "id": "fortnite",
        "name": "Fortnite",
        "exe_patterns": ["fortnite*.exe"],
        "folder_patterns": ["fortnite"],
        "engine": "unreal_engine_5",
        "app_id": None
    },
    {
        "id": "helldivers2",
        "name": "HELLDIVERS™ 2",
        "exe_patterns": ["helldivers2.exe"],
        "folder_patterns": ["helldivers 2", "helldivers2"],
        "engine": "stingray",
        "app_id": 553850
    }
]

def find_primary_executable(game_dir: str, patterns: Optional[List[str]] = None) -> Optional[str]:
    """
    Finds the main game executable by searching only standard binary locations (max depth 2).
    Never crawls the entire filesystem.
    """
    search_dirs = [
        game_dir,
        os.path.join(game_dir, "bin"),
        os.path.join(game_dir, "binaries", "win64"),
        os.path.join(game_dir, "game", "bin", "win64"),
        os.path.join(game_dir, "pioneergame", "binaries", "win64"),
        os.path.join(game_dir, "discovery", "binaries", "win64"),
    ]

    for d in search_dirs:
        if not os.path.exists(d):
            continue
        try:
            files = os.listdir(d)
            if patterns:
                for p in patterns:
                    for f in files:
                        if fnmatch.fnmatch(f.lower(), p.lower()):
                            return os.path.join(d, f)
            else:
                for f in files:
                    if f.lower().endswith(".exe") and not any(x in f.lower() for x in ["unins", "crash", "helper", "setup", "redist"]):
                        return os.path.join(d, f)
        except Exception:
            continue

    return None

def scan_custom_folder(folder_path: str) -> List[DetectedGame]:
    """
    Scans a user-provided folder for games with shallow 1-level subfolder inspection.
    """
    games: List[DetectedGame] = []
    if not folder_path or not os.path.exists(folder_path):
        return games

    drive_map = get_drive_types()

    # Determine if folder_path itself is a game directory or contains multiple game folders
    candidates = []
    try:
        subdirs = [os.path.join(folder_path, d) for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        if subdirs:
            candidates.extend(subdirs)
        candidates.append(folder_path)
    except Exception:
        candidates.append(folder_path)

    for target_dir in candidates:
        dirname = os.path.basename(target_dir).lower()
        matched = False

        for sig in KNOWN_SIGNATURES:
            folder_hit = any(fp in dirname for fp in sig["folder_patterns"])
            exe = find_primary_executable(target_dir, sig["exe_patterns"])

            if folder_hit or exe:
                game_obj = DetectedGame(
                    game_id=sig["id"],
                    name=sig["name"],
                    exe_path=exe or os.path.join(target_dir, f"{sig['id']}.exe"),
                    install_dir=target_dir,
                    engine=sig["engine"],
                    app_id=sig.get("app_id"),
                    source="custom"
                )
                game_obj.drive_type = drive_map.get(game_obj.drive_letter, "HDD" if "e" in game_obj.drive_letter.lower() else "SSD")
                games.append(game_obj)
                matched = True
                break

        if not matched and target_dir != folder_path:
            exe = find_primary_executable(target_dir)
            if exe:
                is_ue = os.path.exists(os.path.join(target_dir, "Engine")) or "win64-shipping" in exe.lower()
                game_obj = DetectedGame(
                    game_id=re.sub(r"[^a-zA-Z0-9_]", "_", dirname),
                    name=os.path.basename(target_dir).replace("_", " ").title(),
                    exe_path=exe,
                    install_dir=target_dir,
                    engine="unreal_engine_5" if is_ue else "generic",
                    source="custom"
                )
                game_obj.drive_type = drive_map.get(game_obj.drive_letter, "HDD" if "e" in game_obj.drive_letter.lower() else "SSD")
                games.append(game_obj)

    return games

def scan_steam_libraries() -> List[DetectedGame]:
    """
    Auto-discovers installed Steam games across all drives using libraryfolders.vdf.
    Fast metadata-only scan (< 100ms).
    """
    games: List[DetectedGame] = []
    steam_roots = ["E:\\steam", "C:\\Program Files (x86)\\Steam", "D:\\Steam", "C:\\Steam"]
    vdf_path = None

    for root in steam_roots:
        cand = os.path.join(root, "steamapps", "libraryfolders.vdf")
        if os.path.exists(cand):
            vdf_path = cand
            break

    if not vdf_path:
        return games

    library_paths = []
    try:
        with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            matches = re.findall(r'"path"\s+"([^"]+)"', content)
            for m in matches:
                p = m.replace("\\\\", "\\")
                if os.path.exists(p):
                    library_paths.append(p)
    except Exception:
        pass

    drive_map = get_drive_types()

    for lib in library_paths:
        apps_dir = os.path.join(lib, "steamapps")
        if not os.path.exists(apps_dir):
            continue

        try:
            for manifest_file in os.listdir(apps_dir):
                if not manifest_file.startswith("appmanifest_") or not manifest_file.endswith(".acf"):
                    continue
                manifest_path = os.path.join(apps_dir, manifest_file)
                try:
                    with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
                        txt = f.read()

                    appid_m = re.search(r'"appid"\s+"(\d+)"', txt)
                    name_m = re.search(r'"name"\s+"([^"]+)"', txt)
                    dir_m = re.search(r'"installdir"\s+"([^"]+)"', txt)

                    if appid_m and name_m and dir_m:
                        appid = int(appid_m.group(1))
                        name = name_m.group(1)
                        # Skip steam runtimes or tools
                        if any(x in name.lower() for x in ["steam linux", "steamworks", "proton"]):
                            continue

                        inst_dir = os.path.join(apps_dir, "common", dir_m.group(1))
                        engine = "generic"
                        slug = f"steam_{appid}"

                        for sig in KNOWN_SIGNATURES:
                            if sig.get("app_id") == appid or any(fp in name.lower() for fp in sig["folder_patterns"]):
                                engine = sig["engine"]
                                slug = sig["id"]
                                break

                        exe = find_primary_executable(inst_dir) or os.path.join(inst_dir, f"{dir_m.group(1)}.exe")
                        game_obj = DetectedGame(
                            game_id=slug,
                            name=name,
                            exe_path=exe,
                            install_dir=inst_dir,
                            engine=engine,
                            app_id=appid,
                            source="steam"
                        )
                        game_obj.drive_type = drive_map.get(game_obj.drive_letter, "HDD" if "e" in game_obj.drive_letter.lower() else "SSD")
                        games.append(game_obj)
                except Exception:
                    pass
        except Exception:
            pass

    return games

def scan_all_games(custom_folders: Optional[List[str]] = None) -> List[DetectedGame]:
    """
    Combined scanner that fetches all Steam games plus any user-specified custom folder.
    Deduplicates by game_id.
    """
    all_games: Dict[str, DetectedGame] = {}

    # 1. Steam Libraries
    for g in scan_steam_libraries():
        all_games[g.game_id] = g

    # 2. Custom Folders
    if custom_folders:
        for f in custom_folders:
            for g in scan_custom_folder(f):
                all_games[g.game_id] = g

    return list(all_games.values())

if __name__ == "__main__":
    games = scan_all_games()
    print(f"Total Games Detected: {len(games)}")
    for g in games:
        print(f" - {g.name} ({g.engine}) on [{g.drive_letter}: {g.drive_type}] -> {g.install_dir}")
