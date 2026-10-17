"""
Mathematical FPS Estimation & Bottleneck Diagnostic Engine for Zabbatha
"""

from typing import Dict, Any

PROFILE_MULTIPLIERS = {
    "cinema_god": 0.65,
    "sweet_spot": 1.0,
    "tryhard_pro": 1.45,
    "stable_60": 0.85,
    "cold_lap": 0.90,
    "batates_pro": 1.90,
    "toaster_god": 2.60
}

RESOLUTION_FACTORS = {
    "1080p": 1.0,
    "1440p": 0.68,
    "4K": 0.40
}

def predict_fps_and_bottleneck(
    hw_specs: Dict[str, Any],
    game_requirements: Dict[str, Any],
    profile_id: str = "sweet_spot",
    resolution: str = "1080p",
    drive_type: str = "SSD"
) -> Dict[str, Any]:
    """
    Calculates expected framerates and identifies hardware bottlenecks.
    """
    user_gpu_score = hw_specs.get("gpu", {}).get("score", 50)
    user_cpu_score = hw_specs.get("cpu", {}).get("score", 50)
    user_vram_gb = hw_specs.get("gpu", {}).get("vram_gb", 6.0)
    user_ram_gb = hw_specs.get("ram", {}).get("total_gb", 16.0)

    rec_gpu = game_requirements.get("rec_gpu_score", 65)
    rec_cpu = game_requirements.get("rec_cpu_score", 65)
    min_vram = 4.0
    rec_vram = 8.0

    # Baseline FPS for recommended hardware at Sweet-Spot 1080p is ~85 FPS
    baseline_fps = 85.0

    # Performance ratio
    gpu_ratio = user_gpu_score / max(1.0, float(rec_gpu))
    cpu_ratio = user_cpu_score / max(1.0, float(rec_cpu))

    # Profile & Resolution scalars
    profile_mult = PROFILE_MULTIPLIERS.get(profile_id, 1.0)
    res_factor = RESOLUTION_FACTORS.get(resolution, 1.0)

    # Effective FPS calculation (GPU dominant with CPU limiting ceiling)
    calculated_avg = baseline_fps * (gpu_ratio ** 0.85) * profile_mult * res_factor
    
    # CPU Bottleneck ceiling
    cpu_max_fps = 60.0 * (cpu_ratio ** 1.1) * (1.3 if profile_id == "tryhard_pro" else 1.0)
    final_avg_fps = min(calculated_avg, cpu_max_fps)
    final_avg_fps = max(15, int(round(final_avg_fps)))

    # 1% Lows calculation (Stability)
    stability_factor = 0.72
    if drive_type == "HDD":
        stability_factor = 0.52 # HDD causes stutter unless cached
    if profile_id == "stable_60":
        stability_factor = 0.88

    one_percent_low = max(10, int(round(final_avg_fps * stability_factor)))

    # Bottleneck Analysis
    bottleneck = "None (Balanced)"
    bottleneck_ar = "متوازن تماماً (لا يوجد عنق زجاجة)"

    if cpu_ratio < gpu_ratio * 0.70:
        bottleneck = "CPU Bound (Processor limits maximum framerate)"
        bottleneck_ar = "محدود بالمعالج (البروسيسور يمنع الكرت من إخراج كامل فريماته)"
    elif gpu_ratio < cpu_ratio * 0.70:
        bottleneck = "GPU Bound (Graphics Card is operating at 100%)"
        bottleneck_ar = "محدود بكرت الشاشة (الكرت يعمل بكامل طاقته)"
    
    # VRAM check for Ultra profiles
    vram_warning = False
    if profile_id in ["cinema_god", "sweet_spot"] and user_vram_gb < 8.0 and resolution in ["1440p", "4K"]:
        vram_warning = True

    # HDD Alert
    hdd_alert = (drive_type == "HDD")

    can_run = (user_gpu_score >= game_requirements.get("min_gpu_score", 30) and 
               user_cpu_score >= game_requirements.get("min_cpu_score", 30))

    return {
        "can_run": can_run,
        "avg_fps": final_avg_fps,
        "one_percent_low": one_percent_low,
        "bottleneck": bottleneck,
        "bottleneck_ar": bottleneck_ar,
        "vram_warning": vram_warning,
        "hdd_alert": hdd_alert,
        "resolution": resolution,
        "profile_id": profile_id
    }
