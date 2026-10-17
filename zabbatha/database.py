"""
Database & Profile Registry Engine for Zabbatha
Defines game metadata, engine parameters, the 7 presets, and emergency packs.
"""

import os
from typing import Dict, Any, List, Optional

PROFILES_INFO = {
    "cinema_god": {
        "id": "cinema_god",
        "name_en": "Cinema-God (Ultra Fidelity)",
        "name_ar": "المتعة البصرية المطلقة (Cinema-God)",
        "desc_en": "4K/1440p Max fidelity, full textures, ray tracing/Lumen, 16x anisotropic filtering.",
        "desc_ar": "أعلى نقاء بصري ممكن، تفاصيل التكستشر كاملة، إضاءة لومن/تتبع أشعة، ثبات 60 فريم.",
        "badge_color": "#8b5cf6" # Vivid purple
    },
    "sweet_spot": {
        "id": "sweet_spot",
        "name_en": "Sweet-Spot (Balanced)",
        "name_ar": "المتوازن الذكي (Sweet-Spot)",
        "desc_en": "Digital Foundry style: High textures, medium heavy effects, zero motion blur, 90-120 FPS.",
        "desc_ar": "توازن مثالي: وضوح بصري فائق، خفض الخيارات الوهمية التي تلتهم الكرت، فريمات عالية.",
        "badge_color": "#10b981" # Emerald green
    },
    "tryhard_pro": {
        "id": "tryhard_pro",
        "name_en": "TryHard Pro (Esports)",
        "name_ar": "الوضع التنافسي (TryHard Pro)",
        "desc_en": "Max FPS, lowest input lag, zero grass/foliage clutter, 1:1 Raw Mouse, sharp visibility.",
        "desc_ar": "أقصى فريمات ممكنة (144-240 FPS)، إزالة العشب لكشف الأعداء، إلغاء تسارع الماوس 1:1.",
        "badge_color": "#06b6d4" # Electric cyan
    },
    "stable_60": {
        "id": "stable_60",
        "name_en": "Stable-60 (Stutter Guard)",
        "name_ar": "حارس الـ 60 فريم (Stable-60)",
        "desc_en": "In-engine framerate limiter, dynamic resolution scaling, eliminates 1% low frame drops.",
        "desc_ar": "ثبات خطي تام عند 60 فريم، منع التقطيع اللحظي (Stutter) باستخدام التحجيم الديناميكي.",
        "badge_color": "#3b82f6" # Neon blue
    },
    "cold_lap": {
        "id": "cold_lap",
        "name_en": "Cold-Lap (Cool & Silent)",
        "name_ar": "لابتوب هادئ وبارد (Cold-Lap)",
        "desc_en": "Caps CPU draw calls, limits power spikes, lowers laptop temperatures by 15-20°C.",
        "desc_ar": "تقليل إجهاد المعالج، كتم صوت المراوح وخفض حرارة اللابتوب من 90°C إلى 70°C.",
        "badge_color": "#0ea5e9" # Ice sky
    },
    "batates_pro": {
        "id": "batates_pro",
        "name_en": "Batates-Pro (Low-End Boost)",
        "name_ar": "البطاطس العملي (Batates-Pro)",
        "desc_en": "Disables shadows, cuts Lumen/volumetrics, FSR Balanced, turns 25 FPS into 60 FPS.",
        "desc_ar": "تصفير الظلال، إلغاء إضاءة لومن الثقيلة، تفعيل FSR، إنقاذ الكروت القديمة (GTX 1050/1650).",
        "badge_color": "#f59e0b" # Warm amber
    },
    "toaster_god": {
        "id": "toaster_god",
        "name_en": "Toaster-God (Extreme Potato)",
        "name_ar": "البطاطس الأسطوري (Toaster-God)",
        "desc_en": "50% resolution scale, LOD bias clay mode, kills all particles. Runs on older relics/iGPUs.",
        "desc_ar": "وضع الآلة الحاسبة: خفض الرندر لـ 50%، تبسيط المضلعات، تشغيل اللعبة على كروت داخلية ميتة.",
        "badge_color": "#ef4444" # Hot red
    }
}

# Concrete Game Profile Definitions
GAME_DATABASE: Dict[str, Any] = {
    "arc_raiders": {
        "id": "arc_raiders",
        "app_id": 1808500,
        "name": "ARC Raiders",
        "engine": "unreal_engine_5",
        "config_paths": {
            "steam": os.path.expandvars(r"%LOCALAPPDATA%\PioneerGame\Saved\Config\WindowsClient"),
            "gamepass": os.path.expandvars(r"%LOCALAPPDATA%\PioneerGame\Saved\Config\WinGDKClient")
        },
        "config_file_name": "GameUserSettings.ini",
        "engine_ini_name": "Engine.ini",
        "requirements": {
            "min_gpu_score": 45, # GTX 1060 / RX 580
            "rec_gpu_score": 70, # RTX 3060 / RX 7600
            "min_cpu_score": 40,
            "rec_cpu_score": 75,
            "min_ram_gb": 12,
            "rec_ram_gb": 16
        },
        "api_fallbacks": {
            "supported": ["dx12", "dx11"],
            "default": "dx12",
            "d3d12_key": "bUseD3D12InGame"
        },
        "presets": {
            "cinema_god": {
                "scalability": {
                    "sg.ResolutionQuality": "100",
                    "sg.ViewDistanceQuality": "3",
                    "sg.AntiAliasingQuality": "3",
                    "sg.ShadowQuality": "3",
                    "sg.GlobalIlluminationQuality": "3",
                    "sg.ReflectionQuality": "3",
                    "sg.PostProcessQuality": "3",
                    "sg.TextureQuality": "3",
                    "sg.EffectsQuality": "3",
                    "sg.FoliageQuality": "3",
                    "sg.ShadingQuality": "3",
                    "sg.LandscapeQuality": "3"
                },
                "embark": {
                    "ResolutionScalingMethod": "Native",
                    "MotionBlurScale": "0.000000",
                    "MotionBlurMode": "Off",
                    "LensDistortionEnabled": "False",
                    "bUseVSync": "False",
                    "bAntiLag2Enabled": "True"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.4",
                    "r.VolumetricFog": "1",
                    "r.Lumen.DiffuseIndirect.Allow": "1",
                    "r.Lumen.Reflections.Allow": "1"
                }
            },
            "sweet_spot": {
                "scalability": {
                    "sg.ResolutionQuality": "100",
                    "sg.ViewDistanceQuality": "2",
                    "sg.AntiAliasingQuality": "2",
                    "sg.ShadowQuality": "2",
                    "sg.GlobalIlluminationQuality": "2",
                    "sg.ReflectionQuality": "1",
                    "sg.PostProcessQuality": "1",
                    "sg.TextureQuality": "3",
                    "sg.EffectsQuality": "1",
                    "sg.FoliageQuality": "1",
                    "sg.ShadingQuality": "2",
                    "sg.LandscapeQuality": "2"
                },
                "embark": {
                    "ResolutionScalingMethod": "FSR",
                    "FSRMode": "Quality",
                    "MotionBlurScale": "0.000000",
                    "MotionBlurMode": "Off",
                    "LensDistortionEnabled": "False",
                    "bUseVSync": "False",
                    "bAntiLag2Enabled": "True"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.6",
                    "r.VolumetricFog": "0",
                    "r.Lumen.DiffuseIndirect.Allow": "1",
                    "r.Lumen.Reflections.Allow": "0"
                }
            },
            "tryhard_pro": {
                "scalability": {
                    "sg.ResolutionQuality": "100",
                    "sg.ViewDistanceQuality": "1",
                    "sg.AntiAliasingQuality": "0",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "2",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0", # Zero grass foliage for competitor visual clarity
                    "sg.ShadingQuality": "0",
                    "sg.LandscapeQuality": "0"
                },
                "embark": {
                    "ResolutionScalingMethod": "FSR",
                    "FSRMode": "Quality",
                    "MotionBlurScale": "0.000000",
                    "MotionBlurMode": "Off",
                    "LensDistortionEnabled": "False",
                    "bUseVSync": "False",
                    "bAntiLag2Enabled": "True",
                    "FrameRateLimit": "240.000000"
                },
                "input_settings": {
                    "RawMouseInputEnabled": "Enabled",
                    "bEnableMouseSmoothing": "False",
                    "bViewAccelerationEnabled": "False"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.75",
                    "r.VolumetricFog": "0",
                    "r.Lumen.DiffuseIndirect.Allow": "0",
                    "r.Lumen.Reflections.Allow": "0",
                    "r.MotionBlurQuality": "0",
                    "r.DepthOfFieldQuality": "0"
                }
            },
            "stable_60": {
                "scalability": {
                    "sg.ResolutionQuality": "90",
                    "sg.ViewDistanceQuality": "1",
                    "sg.AntiAliasingQuality": "1",
                    "sg.ShadowQuality": "1",
                    "sg.GlobalIlluminationQuality": "1",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "1",
                    "sg.TextureQuality": "2",
                    "sg.EffectsQuality": "1",
                    "sg.FoliageQuality": "1",
                    "sg.ShadingQuality": "1",
                    "sg.LandscapeQuality": "1"
                },
                "embark": {
                    "ResolutionScalingMethod": "FSR",
                    "FSRMode": "Quality",
                    "bUseDynamicResolution": "True",
                    "FrameRateLimit": "60.000000",
                    "MotionBlurScale": "0.000000",
                    "MotionBlurMode": "Off",
                    "bUseVSync": "True"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.5",
                    "r.VolumetricFog": "0"
                }
            },
            "cold_lap": {
                "scalability": {
                    "sg.ResolutionQuality": "85",
                    "sg.ViewDistanceQuality": "0",
                    "sg.AntiAliasingQuality": "1",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "2",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0",
                    "sg.ShadingQuality": "0",
                    "sg.LandscapeQuality": "0"
                },
                "embark": {
                    "ResolutionScalingMethod": "FSR",
                    "FSRMode": "Balanced",
                    "FrameRateLimit": "60.000000",
                    "MotionBlurScale": "0.000000",
                    "MotionBlurMode": "Off",
                    "bIdleEnergySavingEnabled": "True"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.5",
                    "r.VolumetricFog": "0",
                    "r.Lumen.DiffuseIndirect.Allow": "0"
                }
            },
            "batates_pro": {
                "scalability": {
                    "sg.ResolutionQuality": "70",
                    "sg.ViewDistanceQuality": "0",
                    "sg.AntiAliasingQuality": "0",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "1",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0",
                    "sg.ShadingQuality": "0",
                    "sg.LandscapeQuality": "0"
                },
                "embark": {
                    "ResolutionScalingMethod": "FSR",
                    "FSRMode": "Performance",
                    "MotionBlurScale": "0.000000",
                    "MotionBlurMode": "Off",
                    "LensDistortionEnabled": "False",
                    "FrameRateLimit": "60.000000"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.7",
                    "r.VolumetricFog": "0",
                    "r.Lumen.DiffuseIndirect.Allow": "0",
                    "r.Lumen.Reflections.Allow": "0",
                    "r.Shadow.DistanceScale": "0.2",
                    "r.Nanite.MaxPixelsPerEdge": "4"
                }
            },
            "toaster_god": {
                "scalability": {
                    "sg.ResolutionQuality": "50",
                    "sg.ViewDistanceQuality": "0",
                    "sg.AntiAliasingQuality": "0",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "0",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0",
                    "sg.ShadingQuality": "0",
                    "sg.LandscapeQuality": "0"
                },
                "embark": {
                    "ResolutionScalingMethod": "FSR",
                    "FSRMode": "UltraPerformance",
                    "MotionBlurScale": "0.000000",
                    "MotionBlurMode": "Off",
                    "LensDistortionEnabled": "False",
                    "FrameRateLimit": "35.000000"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "1.0",
                    "r.VolumetricFog": "0",
                    "r.Lumen.DiffuseIndirect.Allow": "0",
                    "r.Lumen.Reflections.Allow": "0",
                    "r.Shadow.DistanceScale": "0.05",
                    "r.Nanite.MaxPixelsPerEdge": "8",
                    "r.MipMapLODBias": "2"
                }
            }
        }
    },
    "cs2": {
        "id": "cs2",
        "app_id": 730,
        "name": "Counter-Strike 2",
        "engine": "source_2",
        "requirements": {
            "min_gpu_score": 30,
            "rec_gpu_score": 60,
            "min_cpu_score": 35,
            "rec_cpu_score": 70,
            "min_ram_gb": 8,
            "rec_ram_gb": 16
        },
        "api_fallbacks": {
            "supported": ["dx11", "vulkan"],
            "default": "dx11",
            "vulkan_flag": "-vulkan"
        }
    },
    "generic_ue": {
        "id": "generic_ue",
        "name": "Unreal Engine Game",
        "engine": "unreal_engine_5",
        "requirements": {
            "min_gpu_score": 40,
            "rec_gpu_score": 65,
            "min_cpu_score": 40,
            "rec_cpu_score": 65,
            "min_ram_gb": 8,
            "rec_ram_gb": 16
        },
        "config_file_name": "GameUserSettings.ini",
        "engine_ini_name": "Engine.ini",
        "presets": {
            "cinema_god": {
                "scalability": {
                    "sg.ResolutionQuality": "100",
                    "sg.ViewDistanceQuality": "3",
                    "sg.AntiAliasingQuality": "3",
                    "sg.ShadowQuality": "3",
                    "sg.GlobalIlluminationQuality": "3",
                    "sg.ReflectionQuality": "3",
                    "sg.PostProcessQuality": "3",
                    "sg.TextureQuality": "3",
                    "sg.EffectsQuality": "3",
                    "sg.FoliageQuality": "3",
                    "sg.ShadingQuality": "3"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.4",
                    "r.MaxAnisotropy": "16"
                }
            },
            "sweet_spot": {
                "scalability": {
                    "sg.ResolutionQuality": "100",
                    "sg.ViewDistanceQuality": "2",
                    "sg.AntiAliasingQuality": "2",
                    "sg.ShadowQuality": "1",
                    "sg.GlobalIlluminationQuality": "1",
                    "sg.ReflectionQuality": "1",
                    "sg.PostProcessQuality": "1",
                    "sg.TextureQuality": "3",
                    "sg.EffectsQuality": "2",
                    "sg.FoliageQuality": "1",
                    "sg.ShadingQuality": "2"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.5",
                    "r.VolumetricFog": "0",
                    "r.MotionBlurQuality": "0"
                }
            },
            "tryhard_pro": {
                "scalability": {
                    "sg.ResolutionQuality": "100",
                    "sg.ViewDistanceQuality": "1",
                    "sg.AntiAliasingQuality": "0",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "2",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0",
                    "sg.ShadingQuality": "0"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.8",
                    "r.VolumetricFog": "0",
                    "r.MotionBlurQuality": "0",
                    "r.DepthOfFieldQuality": "0",
                    "r.BloomQuality": "0"
                },
                "input_settings": {
                    "bEnableMouseSmoothing": "False",
                    "bViewAccelerationEnabled": "False"
                }
            },
            "stable_60": {
                "scalability": {
                    "sg.ResolutionQuality": "100",
                    "sg.ViewDistanceQuality": "2",
                    "sg.AntiAliasingQuality": "1",
                    "sg.ShadowQuality": "1",
                    "sg.GlobalIlluminationQuality": "1",
                    "sg.ReflectionQuality": "1",
                    "sg.PostProcessQuality": "1",
                    "sg.TextureQuality": "2",
                    "sg.EffectsQuality": "1",
                    "sg.FoliageQuality": "1",
                    "sg.ShadingQuality": "1"
                },
                "engine_cvars": {
                    "t.MaxFPS": "60",
                    "r.MotionBlurQuality": "0"
                }
            },
            "cold_lap": {
                "scalability": {
                    "sg.ResolutionQuality": "90",
                    "sg.ViewDistanceQuality": "1",
                    "sg.AntiAliasingQuality": "1",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "2",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0",
                    "sg.ShadingQuality": "0"
                },
                "engine_cvars": {
                    "t.MaxFPS": "60",
                    "r.VolumetricFog": "0",
                    "r.MotionBlurQuality": "0"
                }
            },
            "batates_pro": {
                "scalability": {
                    "sg.ResolutionQuality": "70",
                    "sg.ViewDistanceQuality": "0",
                    "sg.AntiAliasingQuality": "0",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "1",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0",
                    "sg.ShadingQuality": "0"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "0.7",
                    "r.VolumetricFog": "0",
                    "r.Lumen.DiffuseIndirect.Allow": "0",
                    "r.Lumen.Reflections.Allow": "0",
                    "r.Shadow.DistanceScale": "0.2"
                }
            },
            "toaster_god": {
                "scalability": {
                    "sg.ResolutionQuality": "50",
                    "sg.ViewDistanceQuality": "0",
                    "sg.AntiAliasingQuality": "0",
                    "sg.ShadowQuality": "0",
                    "sg.GlobalIlluminationQuality": "0",
                    "sg.ReflectionQuality": "0",
                    "sg.PostProcessQuality": "0",
                    "sg.TextureQuality": "0",
                    "sg.EffectsQuality": "0",
                    "sg.FoliageQuality": "0",
                    "sg.ShadingQuality": "0"
                },
                "engine_cvars": {
                    "r.tonemapper.sharpen": "1.0",
                    "r.VolumetricFog": "0",
                    "r.Lumen.DiffuseIndirect.Allow": "0",
                    "r.Lumen.Reflections.Allow": "0",
                    "r.Shadow.DistanceScale": "0.05",
                    "r.MipMapLODBias": "2"
                }
            }
        }
    }
}

def get_game_profile(game_id: str, engine: str = "generic") -> Dict[str, Any]:
    """
    Returns specific database definition or generates dynamic fallback template.
    """
    if game_id in GAME_DATABASE:
        return GAME_DATABASE[game_id]
    
    # Generic template fallback with full presets
    generic = dict(GAME_DATABASE["generic_ue"])
    generic["id"] = game_id
    generic["name"] = game_id.replace("_", " ").title()
    generic["engine"] = engine
    return generic

