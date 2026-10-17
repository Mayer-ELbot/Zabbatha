"""
Bilingual Dictionary Engine for Zabbatha (Arabic & English)
"""

STRINGS = {
    "app_title": {
        "en": "Zabbatha Pro - Autonomous Game Optimizer & Deep Engine Tuner",
        "ar": "ظبطها Pro - المحسن الشامل ومحقن إعدادات الألعاب الذكي"
    },
    "app_subtitle": {
        "en": "Deep Engine Tuning • Beyond In-Game Menus • Hardware Prediction",
        "ar": "فرك وتعديل ملفات المحرك • كسر حدود منيو اللعبة • توقع دقيق للفريمات"
    },
    "hardware_specs": {
        "en": "Hardware Deck",
        "ar": "مواصفات الجهاز"
    },
    "system_score": {
        "en": "Hardware Score",
        "ar": "تقييم الهاردوير"
    },
    "detected_games": {
        "en": "Installed Games Deck",
        "ar": "ألعابك المكتشفة"
    },
    "scan_folder_btn": {
        "en": "+ Add Games Folder",
        "ar": "+ إضافة مجلد ألعاب"
    },
    "rescan_btn": {
        "en": "🔄 Rescan All",
        "ar": "🔄 إعادة الفحص"
    },
    "search_placeholder": {
        "en": "Search games by title or engine...",
        "ar": "ابحث عن لعبة أو محرك..."
    },
    "apply_profile": {
        "en": "⚡ Zabbatly (Apply)",
        "ar": "⚡ ظبطهالي (تطبيق)"
    },
    "restore_backup": {
        "en": "↩ Restore Original",
        "ar": "↩ استعادة الإعدادات الأصلية"
    },
    "hdd_savior_tag": {
        "en": "💾 HDD Savior Pack",
        "ar": "💾 حزمة إنقاذ الـ HDD"
    },
    "hdd_savior_tooltip": {
        "en": "Overhauls async texture streaming & shader pre-caching to eliminate stutter on mechanical HDDs.",
        "ar": "يصلح تقطيع وتجمد ألعاب UE5 على الهارد ديسك العادي عبر مضاعفة كاش التكستشر."
    },
    "dx11_tag": {
        "en": "DX11 Fallback",
        "ar": "إجبار ديركت إكس 11"
    },
    "fps_predicted": {
        "en": "Est. FPS",
        "ar": "الفريمات المتوقعة"
    },
    "lows_label": {
        "en": "1% Lows",
        "ar": "أدنى فريمات (استقرار)"
    },
    "engine_label": {
        "en": "Engine",
        "ar": "المحرك"
    },
    "storage_label": {
        "en": "Drive",
        "ar": "القرص"
    },
    "profile_label": {
        "en": "Target Profile",
        "ar": "البروفايل المستهدف"
    },
    "resolution_label": {
        "en": "Resolution",
        "ar": "الدقة"
    },
    "switch_lang": {
        "en": "🌐 العربية",
        "ar": "🌐 English"
    },
    "success_applied": {
        "en": "✅ Successfully applied '{profile}' to {game}! Read-Only guard active.",
        "ar": "✅ تم تطبيق بروفايل '{profile}' على {game} بنجاح! تم تفعيل حماية القفل لمنع اللعبة من مسحه."
    },
    "success_restored": {
        "en": "✅ Restored original configuration for {game}!",
        "ar": "✅ تم استعادة الإعدادات الأصلية للعبة {game} بنجاح!"
    },
    "add_exe_btn": {
        "en": "🎯 Add Game (.exe)",
        "ar": "🎯 إضافة لعبة (.exe)"
    },
    "config_detected": {
        "en": "Auto-Detected Config",
        "ar": "مسار الإعدادات المكتشف"
    },
    "change_config_btn": {
        "en": "✏️ Change",
        "ar": "✏️ تعديل المسار"
    },
    "open_config_btn": {
        "en": "📂 Open Config Dir",
        "ar": "📂 فتح مسار Config"
    }
}

def t(key: str, lang: str = "ar", **kwargs) -> str:
    item = STRINGS.get(key, {})
    val = item.get(lang, item.get("en", key))
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val
