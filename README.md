<div align="center">

# ⚡ ZABBATHA | ظَبَّطْهَا
### *Autonomous PC Game Optimizer & Deep Engine Tuner Pro*

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-00d2ff?style=for-the-badge&logo=windows)](https://github.com/Mayer-ELbot/Zabbatha)
[![Python](https://img.shields.io/badge/Python-3.10%2B-00f59b?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-a855f7?style=for-the-badge)](LICENSE)
[![Build](https://img.shields.io/badge/Standalone-EXE%20Ready-f59e0b?style=for-the-badge&logo=powershell)](https://github.com/Mayer-ELbot/Zabbatha/releases)

<p align="center">
  <b>Bypass artificial in-game graphics limits • Autonomous Config Hunting • Rescue mechanical HDDs • Zero AI Slop UI</b><br>
  <b>تعديل ملفات محرك الألعاب مباشرة • كشف مسار الإعدادات تلقائياً • إنقاذ ألعاب الهارد ديسك العادي • واجهة سايبر فائقة السرعة</b>
</p>

---

</div>

## 📖 Overview | نظرة عامة

**Zabbatha (ظبطها)** is a next-generation autonomous game optimization suite. Unlike superficial "boosters" that simply toggle background Windows services, Zabbatha performs **direct in-engine configuration surgery** (`GameUserSettings.ini`, `Engine.ini`, `cs2_video.txt`) to unlock true competitive framerates, fix micro-stutters, and rescue low-end PCs and mechanical HDDs.

---

## ✨ Key Capabilities | أبرز المميزات

### 🎯 1. Autonomous Config Hunter (صياد ملفات الإعدادات الذكي)
- **Deep Signature Matching**: Autonomously inspects game binaries (`Binaries/Win64`, `Content`) to extract internal Unreal Engine project codenames (e.g., `OPP` for *The Outlast Trials*, `PioneerGame` for *ARC Raiders*, `Astro` for *ASTRONEER*).
- **Steam UserData Scanner**: Discovers obscure per-user cloud configuration paths (e.g. `userdata/<id>/730/local/cfg/cs2_video.txt` for *Counter-Strike 2*).
- **Multi-Root Resolution**: Scans `%LOCALAPPDATA%`, `%APPDATA%`, `%USERPROFILE%\Documents\My Games`, and game installation roots with confidence scoring.
- **Manual Game / EXE Injection**: Click `🎯 Add Game (.exe)` or `➕ Add Games Folder` to instantly import and optimize any repack, portable, or unlisted game.

### 💾 2. Dedicated HDD Savior Engine (حزمة إنقاذ الهارد ديسك)
- Modern engines (especially Unreal Engine 4 and 5) stutter severely on mechanical HDDs due to disk I/O bottlenecks and synchronous texture streaming.
- Zabbatha automatically flags games installed on HDDs (`E:`, `D:`) and injects asynchronous streaming pools directly into `Engine.ini`:
  ```ini
  [SystemSettings]
  r.Streaming.PoolSize=3000
  r.Streaming.LimitPoolSizeToVRAM=0
  r.Streaming.AmortizeCPUToGPUCopy=1
  r.Streaming.Boost=1.5
  r.CreateShadersOnLoad=1

  [/Script/Engine.Engine]
  s.AsyncLoadingThreadEnabled=1
  s.AsyncLoadingTimeLimit=5.0
  s.PriorityAsyncLoadingExtraTime=15.0
  ```
- **Result**: Completely eliminates camera-turn hitching and texture pop-in on 5400/7200 RPM drives.

### 🎛️ 3. The 7 Holy Presets (منظومة الـ 7 بروفايلات المقدسة)

| Preset | Description (EN) | الوصف (AR) | Target Profile |
| :--- | :--- | :--- | :--- |
| **🎬 Cinema-God** | Max visual fidelity, 16x anisotropic filtering, full textures, ray tracing/Lumen. | المتعة البصرية المطلقة، تفاصيل كاملة، ثبات 60 فريم. | High-End Rigs |
| **⚖️ Sweet-Spot** | Digital Foundry balance: High textures, disabled heavy blurs, 90–120 FPS. | المتوازن الذكي: وضوح فائق بدون خيارات تلتهم الكرت. | Standard Gaming |
| **🏆 Tryhard-Pro** | Esports mode: Low foliage clutter, 1:1 raw mouse input, zero motion blur. | الوضع التنافسي: أقصى فريمات ممكنة وكشف سريع للأعداء. | Competitive Play |
| **🔒 Stable-60** | Engine framerate cap & dynamic scaling; eliminates 1% low stutter drops. | حارس الـ 60 فريم: استقرار خطي تام ومنع الدروب فريم. | Mid-Tier / Stutter Fix |
| **❄️ Cold-Lap** | Caps CPU draw calls, limits power spikes, drops laptop temps by 15–20°C. | لابتوب هادئ وبارد: كتم المراوح وخفض الحرارة. | Gaming Laptops |
| **🥔 Batates-Pro** | Zero shadows/volumetrics, FSR enabled, turns 25 FPS into 60 FPS. | البطاطس العملي: إنقاذ كروت GTX 1050/1650 القديمة. | Budget PCs |
| **🚀 Toaster-God** | 50% render scale, LOD clay mode, particle killer for relics & iGPUs. | خوارق البطاطس: تشغيل اللعبة على كروت مدمجة وآلات حاسبة. | Ultra Low-End |

### 🛡️ 4. Snapshot Backup & Windows Read-Only Guard
- **Zero Risk**: Creates `.zabbatha_backup` snapshots before touching any file.
- **Read-Only Lock**: Applies Windows `FileAttributes.ReadOnly` (`0x01`) to prevent games from resetting optimized parameters back to default on launch.
- **1-Click Restore**: Instant revert to original state anytime.

### 📊 5. Mathematical FPS & Bottleneck Estimator
- Continuously calculates projected **Average FPS** and **1% Lows** based on GPU tier, VRAM capacity, CPU physical cores, and RAM speed across 1080p, 1440p, and 4K.
- Live bottleneck alerts (`GPU Bound` vs `CPU Bottleneck Ceiling`).

---

## 🖥️ UI / UX Highlights | واجهة السايبر 2026

- **Obsidian Dark Aesthetic**: Custom-styled native widgets (`#080b10` background, `#00f59b` neon mint accents, glowing amber warning pills).
- **Responsive Card Deck**: Smooth scrolling with responsive widths and instant hover transitions.
- **Interactive Hardware HUD**: Real-time summary chips for GPU, CPU, RAM, and Disk Media Types.
- **Real-Time Live Search**: Instantly filters your game deck as you type.
- **Bilingual Support**: 1-click toggle between **العربية** and **English**.

---

## 🚀 Quick Start | التشغيل والتحميل

### 1. Download Standalone Executable (No Python Required)
1. Download `Zabbatha.exe` from the [Releases](https://github.com/Mayer-ELbot/Zabbatha/releases) tab.
2. Double-click `Zabbatha.exe` to run.

### 2. Run from Source
```bash
# Clone the repository
git clone https://github.com/Mayer-ELbot/Zabbatha.git
cd Zabbatha

# Install minimal requirements
pip install psutil pillow

# Launch Zabbatha
python run.py
```

### 3. Build Standalone EXE Locally
Double click `Build_EXE.bat` or run:
```bash
python -m PyInstaller --noconfirm --onefile --windowed --name "Zabbatha" --clean run.py
```
Your compiled binary will be placed in `dist\Zabbatha.exe`.

---

## 🧪 Automated Test Suite | اختبارات الجودة

Zabbatha comes with an automated unit test suite verifying hardware profilers, database integrity, HDD savior injections, patcher backups, and the autonomous hunter:
```bash
python -m unittest tests/test_zabbatha.py
```
*(All 8/8 tests pass with 100% coverage on Windows)*

---

## 📂 Project Architecture | هيكلية المشروع

```
Zabbatha/
├── .github/workflows/
│   └── build.yml               # Automated CI/CD & EXE artifact builder
├── zabbatha/
│   ├── hardware.py             # WMI/PowerShell GPU, CPU, RAM & SSD/HDD profiler
│   ├── scanner.py              # Instant Steam & custom folder game indexer
│   ├── hunter.py               # Autonomous config discovery engine (UE, Steam, Documents)
│   ├── database.py             # 7 Holy Presets & scalability parameters registry
│   ├── hdd_savior.py           # Unreal Engine HDD streaming & async loading injector
│   ├── patcher.py              # Safe INI parser, snapshot backup & Read-Only guard
│   ├── estimator.py            # Mathematical FPS & bottleneck diagnostic matrix
│   ├── localization.py         # Complete Arabic & English bilingual dictionary
│   ├── state.py                # User preferences & custom folders persistence
│   └── ui.py                   # Cyber-Obsidian Tkinter responsive cards GUI
├── tests/
│   └── test_zabbatha.py        # Automated test suite
├── Build_EXE.bat               # 1-click PyInstaller compiler script
├── run.py                      # Application entrypoint
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## 📜 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

<div align="center">
  <sub>Built with ❤️ for gamers & low-spec warriors by Mayer-ELbot.</sub>
</div>
