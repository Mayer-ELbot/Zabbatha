"""
State & Preferences Manager for Zabbatha
"""

import os
import json
from typing import Dict, Any, List

CONFIG_FILE = "zabbatha_config.json"

class AppState:
    def __init__(self):
        self.lang = "ar"
        self.custom_folders: List[str] = []
        self.game_settings: Dict[str, Dict[str, Any]] = {}
        self.load()

    def get_game_pref(self, game_id: str) -> Dict[str, Any]:
        if game_id not in self.game_settings:
            self.game_settings[game_id] = {
                "profile": "sweet_spot",
                "resolution": "1080p",
                "hdd_savior": True,
                "dx11": False
            }
        return self.game_settings[game_id]

    def set_game_pref(self, game_id: str, key: str, value: Any):
        if game_id not in self.game_settings:
            self.get_game_pref(game_id)
        self.game_settings[game_id][key] = value
        self.save()

    def add_custom_folder(self, folder: str):
        if folder and os.path.exists(folder) and folder not in self.custom_folders:
            self.custom_folders.append(folder)
            self.save()

    def remove_custom_folder(self, folder: str):
        if folder in self.custom_folders:
            self.custom_folders.remove(folder)
            self.save()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.lang = data.get("lang", "ar")
                    self.custom_folders = data.get("custom_folders", [])
                    self.game_settings = data.get("game_settings", {})
            except Exception:
                pass

    def save(self):
        try:
            data = {
                "lang": self.lang,
                "custom_folders": self.custom_folders,
                "game_settings": self.game_settings
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

STATE = AppState()
