"""
HDD Savior Engine for Zabbatha
Optimizes Unreal Engine and modern game streaming pipelines for 5400/7200 RPM mechanical HDDs.
Eliminates camera-turn stutter, streaming micro-freezes, and asset pop-in.
"""

import os
from typing import Dict, List, Tuple

HDD_SYSTEM_SETTINGS = {
    "r.Streaming.PoolSize": "3000",
    "r.Streaming.LimitPoolSizeToVRAM": "0",
    "r.Streaming.AmortizeCPUToGPUCopy": "1",
    "r.Streaming.Boost": "1.5",
    "r.Streaming.HLODStrategy": "2",
    "r.CreateShadersOnLoad": "1",
}

HDD_ENGINE_SETTINGS = {
    "s.AsyncLoadingThreadEnabled": "1",
    "s.AsyncLoadingTimeLimit": "5.0",
    "s.PriorityAsyncLoadingExtraTime": "15.0",
    "s.LevelStreamingActorsUpdateTimeLimit": "5.0"
}

def inject_hdd_savior_to_engine_ini(engine_ini_path: str) -> Tuple[bool, str]:
    """
    Safely injects or updates HDD streaming parameters inside Engine.ini.
    """
    try:
        os.makedirs(os.path.dirname(engine_ini_path), exist_ok=True)
        lines: List[str] = []
        if os.path.exists(engine_ini_path):
            with open(engine_ini_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

        # Parse sections
        sections: Dict[str, Dict[str, str]] = {}
        current_section = ""
        header_order = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped
                if current_section not in sections:
                    sections[current_section] = {}
                    header_order.append(current_section)
            elif "=" in stripped and not stripped.startswith(";"):
                k, v = stripped.split("=", 1)
                if current_section:
                    sections[current_section][k.strip()] = v.strip()

        # Ensure [SystemSettings] exists
        sys_sec = "[SystemSettings]"
        if sys_sec not in sections:
            sections[sys_sec] = {}
            header_order.append(sys_sec)
        for k, v in HDD_SYSTEM_SETTINGS.items():
            sections[sys_sec][k] = v

        # Ensure [/Script/Engine.Engine] exists
        eng_sec = "[/Script/Engine.Engine]"
        if eng_sec not in sections:
            sections[eng_sec] = {}
            header_order.append(eng_sec)
        for k, v in HDD_ENGINE_SETTINGS.items():
            sections[eng_sec][k] = v

        # Write back
        new_content = []
        for sec in header_order:
            new_content.append(f"{sec}\n")
            for k, v in sections[sec].items():
                new_content.append(f"{k}={v}\n")
            new_content.append("\n")

        with open(engine_ini_path, "w", encoding="utf-8") as f:
            f.writelines(new_content)

        return True, "HDD Savior Pack injected into Engine.ini successfully."
    except Exception as ex:
        return False, f"Failed injecting HDD Savior: {str(ex)}"
