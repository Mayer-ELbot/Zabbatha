"""
Hardware Detection Engine for Zabbatha
Detects GPU, VRAM, CPU, RAM, and identifies Drive Types (SSD vs HDD).
"""

import os
import re
import sys
import platform
import subprocess
import psutil
from typing import Dict, Any, List

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
_CACHED_DRIVES = None
_CACHED_SPECS = None

def get_drive_types() -> Dict[str, str]:
    """
    Detects whether partitions (C:, D:, E:, etc.) reside on an SSD or HDD.
    Uses PowerShell Get-PhysicalDisk without flashing console window. Cached in memory.
    """
    global _CACHED_DRIVES
    if _CACHED_DRIVES is not None:
        return dict(_CACHED_DRIVES)

    drive_types: Dict[str, str] = {}
    try:
        cmd = (
            'Get-Partition | Select-Object DriveLetter, DiskNumber | '
            'ForEach-Object { '
            '  $letter = $_.DriveLetter; '
            '  $disk = $_.DiskNumber; '
            '  if ($letter) { '
            '    $media = (Get-PhysicalDisk | Where-Object DeviceId -eq $disk).MediaType; '
            '    "$letter=$media" '
            '  } '
            '}'
        )
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=5,
            creationflags=CREATE_NO_WINDOW
        )
        for line in res.stdout.strip().splitlines():
            line = line.strip()
            if "=" in line:
                drv, media = line.split("=", 1)
                drv = drv.strip().upper()
                media = media.strip().upper()
                if "SSD" in media:
                    drive_types[drv] = "SSD"
                elif "HDD" in media:
                    drive_types[drv] = "HDD"
                else:
                    drive_types[drv] = media if media else "Unknown"
    except Exception:
        pass

    # Fallback for partitions
    for p in psutil.disk_partitions(all=False):
        letter = p.mountpoint.split(":")[0].upper()
        if letter and letter not in drive_types:
            drive_types[letter] = "SSD" if "c" in letter.lower() else "HDD"

    _CACHED_DRIVES = dict(drive_types)
    return drive_types

def get_gpu_info() -> Dict[str, Any]:
    """
    Detects primary GPU and Dedicated Video RAM via PowerShell / WMI.
    """
    gpu_name = "Generic Display Adapter"
    vram_bytes = 0
    driver_version = "Unknown"

    try:
        cmd = (
            'Get-CimInstance Win32_VideoController | '
            'Select-Object Name, AdapterRAM, DriverVersion | '
            'ForEach-Object { "$($_.Name);$($_.AdapterRAM);$($_.DriverVersion)" }'
        )
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=5,
            creationflags=CREATE_NO_WINDOW
        )
        for line in res.stdout.strip().splitlines():
            parts = line.strip().split(";")
            if len(parts) >= 2:
                name = parts[0].strip()
                # Ignore virtual displays if physical exists
                if any(x in name.lower() for x in ["basic", "rdp", "virtual"]) and gpu_name != "Generic Display Adapter":
                    continue
                gpu_name = name
                try:
                    vram_bytes = max(vram_bytes, int(parts[1]))
                except Exception:
                    pass
                if len(parts) >= 3:
                    driver_version = parts[2].strip()
    except Exception:
        pass

    # Fallback estimation for modern 64-bit GPUs if AdapterRAM capped at 4GB in 32-bit WMI
    vram_gb = round(vram_bytes / (1024**3), 1)
    if vram_gb <= 4.0:
        # Check if high-end card whose VRAM is known
        lower_name = gpu_name.lower()
        if "7600" in lower_name or "4060" in lower_name or "3060" in lower_name or "2060 super" in lower_name:
            vram_gb = 8.0
        elif "3060 12gb" in lower_name:
            vram_gb = 12.0
        elif "6700" in lower_name or "7700" in lower_name:
            vram_gb = 12.0
        elif "4070" in lower_name:
            vram_gb = 12.0
        elif "4080" in lower_name:
            vram_gb = 16.0
        elif "1650" in lower_name or "1050 ti" in lower_name or "570" in lower_name:
            vram_gb = 4.0
        elif "1060 6gb" in lower_name:
            vram_gb = 6.0
        elif "vega" in lower_name or "uhd" in lower_name or "iris" in lower_name:
            vram_gb = 2.0

    # Calculate GPU Performance Tier (1 - 100)
    score = 30
    lower = gpu_name.lower()
    if any(x in lower for x in ["4090", "7900 xtx"]):
        score = 98
    elif any(x in lower for x in ["4080", "7900 xt"]):
        score = 92
    elif any(x in lower for x in ["4070 ti", "7800 xt", "3080 ti", "3090"]):
        score = 86
    elif any(x in lower for x in ["4070", "3080", "6800 xt"]):
        score = 82
    elif any(x in lower for x in ["4060 ti", "3070", "6700 xt", "7700 xt"]):
        score = 76
    elif any(x in lower for x in ["4060", "7600", "3060 ti", "6650 xt"]):
        score = 72
    elif any(x in lower for x in ["3060", "6600", "2070", "2060 super", "5700 xt"]):
        score = 64
    elif any(x in lower for x in ["2060", "1660 ti", "1660 super", "5600 xt"]):
        score = 54
    elif any(x in lower for x in ["1660", "1060 6gb", "rx 580", "rx 590"]):
        score = 46
    elif any(x in lower for x in ["1650", "1050 ti", "rx 570", "rx 5500"]):
        score = 36
    elif any(x in lower for x in ["1050", "rx 560", "gtx 960", "gtx 750 ti"]):
        score = 26
    elif any(x in lower for x in ["vega", "iris", "uhd 770", "uhd 730"]):
        score = 18
    else:
        # Estimation by VRAM
        if vram_gb >= 8: score = 65
        elif vram_gb >= 6: score = 50
        elif vram_gb >= 4: score = 35
        else: score = 15

    return {
        "name": gpu_name,
        "vram_gb": vram_gb,
        "driver": driver_version,
        "score": score
    }

def get_cpu_info() -> Dict[str, Any]:
    """
    Detects CPU model, cores, and estimates performance tier.
    """
    name = platform.processor() or "Modern x64 Processor"
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
    except Exception:
        pass

    physical_cores = psutil.cpu_count(logical=False) or 4
    logical_cores = psutil.cpu_count(logical=True) or 8

    # Scoring
    score = 40
    lower = name.lower()
    if any(x in lower for x in ["7800x3d", "7950x3d", "14900k", "13900k"]):
        score = 98
    elif any(x in lower for x in ["7600x", "7700x", "14700k", "13700k", "14600k", "13600k", "5800x3d"]):
        score = 88
    elif any(x in lower for x in ["8400f", "7500f", "7600", "5700x", "12600k", "12700k", "13400", "14400"]):
        score = 80
    elif any(x in lower for x in ["5600x", "5600", "12400", "11600k", "10700k"]):
        score = 70
    elif any(x in lower for x in ["3600", "3700x", "10400", "11400", "9700k"]):
        score = 55
    elif any(x in lower for x in ["2600", "1600", "8400", "9400", "7700k"]):
        score = 42
    elif physical_cores >= 8:
        score = 65
    elif physical_cores >= 6:
        score = 55
    else:
        score = 30

    return {
        "name": name.strip(),
        "physical_cores": physical_cores,
        "logical_cores": logical_cores,
        "score": score
    }

def get_system_specs(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Aggregates full system specs for Zabbatha's estimation matrix.
    Cached in memory to eliminate repeated PowerShell/WMI calls.
    """
    global _CACHED_SPECS
    if _CACHED_SPECS is not None and not force_refresh:
        return dict(_CACHED_SPECS)

    gpu = get_gpu_info()
    cpu = get_cpu_info()
    ram = psutil.virtual_memory()
    total_ram_gb = round(ram.total / (1024**3), 1)
    avail_ram_gb = round(ram.available / (1024**3), 1)
    drives = get_drive_types()

    # Overall System Hardware Score (Weighted: 65% GPU, 25% CPU, 10% RAM)
    ram_score = min(100, int((total_ram_gb / 32.0) * 100))
    overall_score = int((gpu["score"] * 0.65) + (cpu["score"] * 0.25) + (ram_score * 0.10))

    _CACHED_SPECS = {
        "gpu": gpu,
        "cpu": cpu,
        "ram": {
            "total_gb": total_ram_gb,
            "avail_gb": avail_ram_gb,
            "score": ram_score
        },
        "drives": drives,
        "overall_score": overall_score,
        "os": f"Windows {platform.version()}"
    }
    return dict(_CACHED_SPECS)

if __name__ == "__main__":
    import json
    specs = get_system_specs()
    print(json.dumps(specs, indent=2))
