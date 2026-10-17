"""
Zabbatha (ظبطها) - 2026 Modern Desktop Suite
Built with CustomTkinter for native dark-mode Windows UI (Zero AI Slop, No PowerShell Popups).
Features Games Library, Autonomous Config Hunter, Hardware HUD, and Steam & DLC Hub (GreenLuma integration).
"""

import os
import sys
import re
import subprocess
import ctypes
import customtkinter as ctk
from tkinter import filedialog
from typing import List, Dict, Any, Optional

from .hardware import get_system_specs
from .scanner import scan_all_games, scan_custom_folder, DetectedGame
from .database import get_game_profile, PROFILES_INFO
from .patcher import apply_game_profile, restore_game_backup, resolve_game_config_dir
from .hunter import find_game_config_autonomously
from .estimator import predict_fps_and_bottleneck
from .localization import t, STRINGS
from .state import AppState
from .steam_hub import (
    get_steam_path,
    get_steam_users,
    generate_greenluma_applist,
    launch_game_optimized
)

# High DPI Awareness on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

# Palette Constants
C_BG_ROOT = "#0c0e14"
C_BG_SIDEBAR = "#11141c"
C_BG_CARD = "#161a24"
C_BG_INNER = "#10131a"
C_BORDER = "#232a3a"
C_ACCENT_GREEN = "#00f59b"
C_ACCENT_CYAN = "#00d2ff"
C_ACCENT_AMBER = "#f59e0b"
C_ACCENT_PURPLE = "#a855f7"
C_ACCENT_RED = "#ef4444"
C_TEXT_WHITE = "#ffffff"
C_TEXT_GRAY = "#94a3b8"
C_TEXT_MUTED = "#64748b"

PRESET_KEYS = [
    "cinema_god",
    "sweet_spot",
    "tryhard_pro",
    "stable_60",
    "cold_lap",
    "batates_pro",
    "toaster_god"
]

PRESET_DISPLAY_NAMES = {
    "cinema_god": {"en": "🎬 Cinema-God", "ar": "🎬 المتعة البصرية"},
    "sweet_spot": {"en": "⚖️ Sweet-Spot", "ar": "⚖️ المتوازن الذكي"},
    "tryhard_pro": {"en": "🏆 Tryhard-Pro", "ar": "🏆 الوضع التنافسي"},
    "stable_60": {"en": "🔒 Stable-60", "ar": "🔒 حارس الـ 60"},
    "cold_lap": {"en": "❄️ Cold-Lap", "ar": "❄️ لابتوب بارد"},
    "batates_pro": {"en": "🥔 Batates-Pro", "ar": "🥔 بطاطس برو"},
    "toaster_god": {"en": "🚀 Toaster-God", "ar": "🚀 خوارق البطاطس"}
}

class ZabbathaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zabbatha (ظبطها) - Autonomous Game Optimizer & Deep Engine Tuner Pro")
        self.geometry("1280x880")
        self.minsize(1080, 720)
        self.configure(fg_color=C_BG_ROOT)

        # State & Hardware
        self.state = AppState()
        self.specs = get_system_specs()
        self.hw_score = self.specs.get("overall_score", 71)
        self.games: List[DetectedGame] = []
        self.filtered_games: List[DetectedGame] = []

        # Filters
        self.search_query = ""
        self.active_filter = "All"
        self.current_view = "library"

        # Toast manager
        self.toast_widget: Optional[ctk.CTkFrame] = None
        self.toast_timer = None

        # Build Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Initial Scan
        self.rescan_games()

    def _build_sidebar(self):
        """Modern Sleek Left Navigation Sidebar"""
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=C_BG_SIDEBAR,
            border_width=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # Branding Header
        brand_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(20, 16))

        logo_lbl = ctk.CTkLabel(
            brand_frame,
            text="⚡ ZABBATHA",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=C_ACCENT_GREEN
        )
        logo_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            brand_frame,
            text="Autonomous Engine Tuner",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=C_TEXT_MUTED
        )
        sub_lbl.pack(anchor="w")

        # Rig Score Chip in Sidebar
        gpu_short = self.specs.get("gpu", {}).get("name", "GPU")
        if len(gpu_short) > 22:
            gpu_short = gpu_short[:22] + "..."

        score_box = ctk.CTkFrame(self.sidebar_frame, fg_color="#0d2319", corner_radius=8, border_width=1, border_color="#10b981")
        score_box.pack(fill="x", padx=16, pady=(0, 20))

        score_lbl = ctk.CTkLabel(
            score_box,
            text=f"🔥 Rig Score: {self.hw_score}/100",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=C_ACCENT_GREEN
        )
        score_lbl.pack(pady=(6, 2))

        gpu_lbl = ctk.CTkLabel(
            score_box,
            text=f"🎮 {gpu_short}",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#a7f3d0"
        )
        gpu_lbl.pack(pady=(0, 6))

        # Nav Buttons
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        nav_items = [
            ("library", t("nav_library", self.state.lang)),
            ("hardware", t("nav_hardware", self.state.lang)),
            ("steam_hub", t("nav_steam_hub", self.state.lang)),
            ("settings", t("nav_settings", self.state.lang))
        ]

        for view_key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f"  {label}",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="#172033" if view_key == "library" else "transparent",
                text_color=C_TEXT_WHITE if view_key == "library" else C_TEXT_GRAY,
                hover_color="#1f293d",
                command=lambda vk=view_key: self.show_view(vk)
            )
            btn.pack(fill="x", padx=14, pady=4)
            self.nav_buttons[view_key] = btn

        # Language Selector at Bottom of Sidebar
        bottom_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_box.pack(side="bottom", fill="x", padx=16, pady=16)

        lang_label = ctk.CTkLabel(
            bottom_box,
            text="Language / اللغة:",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=C_TEXT_MUTED
        )
        lang_label.pack(anchor="w", pady=(0, 4))

        self.lang_seg = ctk.CTkSegmentedButton(
            bottom_box,
            values=["English", "العربية"],
            command=self._on_language_changed,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
        )
        self.lang_seg.pack(fill="x")
        self.lang_seg.set("English" if self.state.lang == "en" else "العربية")

    def _build_content_area(self):
        """Right Content Container with Swappable View Frames"""
        self.content_container = ctk.CTkFrame(self, fg_color=C_BG_ROOT, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # 4 Main Views
        self.views: Dict[str, ctk.CTkFrame] = {}
        self.views["library"] = self._build_library_view()
        self.views["hardware"] = self._build_hardware_view()
        self.views["steam_hub"] = self._build_steam_hub_view()
        self.views["settings"] = self._build_settings_view()

        self.show_view("library")

    def show_view(self, view_key: str):
        self.current_view = view_key

        # Highlight active nav button
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(fg_color="#1e293b", text_color=C_ACCENT_GREEN)
            else:
                btn.configure(fg_color="transparent", text_color=C_TEXT_GRAY)

        # Show selected frame
        for k, frame in self.views.items():
            if k == view_key:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

    # ==========================================
    # VIEW 1: GAME LIBRARY (DECK)
    # ==========================================
    def _build_library_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self.content_container, fg_color=C_BG_ROOT, corner_radius=0)

        # Top Control Bar
        top_bar = ctk.CTkFrame(view, fg_color=C_BG_ROOT, height=60)
        top_bar.pack(fill="x", padx=20, pady=(16, 10))

        # Search Box
        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text=t("search_placeholder", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=320,
            height=38,
            corner_radius=8,
            fg_color=C_BG_CARD,
            border_color=C_BORDER,
            text_color=C_TEXT_WHITE
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        # Filter Chips Segmented Button
        self.filter_seg = ctk.CTkSegmentedButton(
            top_bar,
            values=["All", "⚠️ HDD", "⚡ Unreal", "Steam"],
            command=self._on_filter_changed,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.filter_seg.pack(side="left", padx=(0, 12))
        self.filter_seg.set("All")

        # Action Buttons on Right
        actions_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        actions_frame.pack(side="right")

        self.btn_add_exe = ctk.CTkButton(
            actions_frame,
            text=t("add_exe_btn", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#3730a3",
            hover_color="#4338ca",
            height=36,
            corner_radius=8,
            command=self.pick_and_add_exe
        )
        self.btn_add_exe.pack(side="left", padx=4)

        self.btn_add_folder = ctk.CTkButton(
            actions_frame,
            text=t("scan_folder_btn", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#1e3a8a",
            hover_color="#2563eb",
            height=36,
            corner_radius=8,
            command=self.pick_and_scan_folder
        )
        self.btn_add_folder.pack(side="left", padx=4)

        self.btn_rescan = ctk.CTkButton(
            actions_frame,
            text="🔄 Rescan",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#1e293b",
            hover_color="#334155",
            height=36,
            width=80,
            corner_radius=8,
            command=self.rescan_games
        )
        self.btn_rescan.pack(side="left", padx=4)

        # Status & Count Header Strip
        status_strip = ctk.CTkFrame(view, fg_color="transparent", height=24)
        status_strip.pack(fill="x", padx=20, pady=(0, 8))

        self.lbl_game_count = ctk.CTkLabel(
            status_strip,
            text="Indexing installed games...",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=C_ACCENT_GREEN
        )
        self.lbl_game_count.pack(side="left")

        # Scrollable Cards Container
        self.cards_scroll = ctk.CTkScrollableFrame(
            view,
            fg_color=C_BG_ROOT,
            corner_radius=0
        )
        self.cards_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        return view

    def _on_search_key(self, event):
        self.search_query = self.search_entry.get().strip().lower()
        self._filter_and_render()

    def _on_filter_changed(self, value):
        self.active_filter = value
        self._filter_and_render()

    def _filter_and_render(self):
        filtered = []
        for g in self.games:
            if self.search_query:
                q = self.search_query
                m_name = q in g.name.lower()
                m_eng = q in g.engine.lower()
                m_dir = q in g.install_dir.lower()
                if not (m_name or m_eng or m_dir):
                    continue

            if self.active_filter == "⚠️ HDD" and g.drive_type != "HDD":
                continue
            if self.active_filter == "⚡ Unreal" and "unreal" not in g.engine.lower():
                continue
            if self.active_filter == "Steam" and g.source != "steam":
                continue

            filtered.append(g)

        self.filtered_games = filtered
        self.render_game_cards()

    def pick_and_add_exe(self):
        """Points directly to any game executable and indexes it with the hunter."""
        selected_file = filedialog.askopenfilename(
            title="Select Game Binary (اختر ملف تشغيل اللعبة)",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if not selected_file or not os.path.exists(selected_file):
            return

        install_dir = os.path.dirname(selected_file)
        exe_file = os.path.basename(selected_file)
        base_name = os.path.splitext(exe_file)[0]
        game_name = base_name.replace("_", " ").replace("-", " ").title()
        slug = re.sub(r"[^a-zA-Z0-9_]", "_", base_name.lower())

        is_ue = (
            os.path.exists(os.path.join(install_dir, "Engine")) or
            os.path.exists(os.path.join(install_dir, "..", "Engine")) or
            "shipping" in exe_file.lower() or
            "win64" in install_dir.lower()
        )

        from .hardware import get_drive_types
        drive_map = get_drive_types()
        drive_letter = os.path.splitdrive(install_dir)[0].replace(":", "").upper()
        drive_type = drive_map.get(drive_letter, "HDD" if "e" in drive_letter.lower() else "SSD")

        game_obj = DetectedGame(
            game_id=slug,
            name=game_name,
            exe_path=selected_file,
            install_dir=install_dir,
            engine="unreal_engine_5" if is_ue else "generic",
            source="custom_exe"
        )
        game_obj.drive_type = drive_type

        # Autonomous Hunt
        hunt_res = find_game_config_autonomously(
            slug, game_name, install_dir=install_dir, exe_path=selected_file, engine_hint=game_obj.engine
        )
        if hunt_res.config_dir:
            self.state.set_game_pref(slug, "custom_config_dir", hunt_res.config_dir)

        self.games = [g for g in self.games if g.game_id != slug]
        self.games.insert(0, game_obj)
        self.state.add_custom_folder(install_dir)

        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, game_name)
        self.search_query = game_name.lower()
        self.show_toast(f"Added '{game_name}'! Config auto-detected: {hunt_res.source}", "success")
        self._filter_and_render()

    def pick_and_scan_folder(self):
        """Scans any user provided games directory."""
        selected_dir = filedialog.askdirectory(title="Select Games Directory (اختر مجلد الألعاب)")
        if not selected_dir:
            return

        self.state.add_custom_folder(selected_dir)
        new_games = scan_custom_folder(selected_dir)
        if not new_games:
            self.show_toast(f"No game binaries found in '{selected_dir}'", "warning")
            return

        existing_ids = {g.game_id for g in self.games}
        added = 0
        for g in new_games:
            if g.game_id not in existing_ids:
                self.games.append(g)
                existing_ids.add(g.game_id)
                added += 1

        self.show_toast(f"Added {added} game card(s) from '{os.path.basename(selected_dir)}'!", "success")
        self._filter_and_render()

    def rescan_games(self):
        """Indexes all games silently."""
        self.games = scan_all_games(self.state.custom_folders)
        self.filtered_games = list(self.games)
        self._filter_and_render()
        self.show_toast(f"Indexed {len(self.games)} games across all libraries.", "info")

    def render_game_cards(self):
        """Renders responsive CustomTkinter game cards"""
        for w in self.cards_scroll.winfo_children():
            w.destroy()

        total = len(self.games)
        showing = len(self.filtered_games)
        self.lbl_game_count.configure(text=f"Showing: {showing} of {total} Detected Games")

        if not self.filtered_games:
            empty_box = ctk.CTkFrame(self.cards_scroll, fg_color="transparent", height=200)
            empty_box.pack(fill="x", pady=60)
            ctk.CTkLabel(
                empty_box,
                text="🎮 No matching games found",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=C_TEXT_GRAY
            ).pack()
            ctk.CTkLabel(
                empty_box,
                text="Use '+ Add Games Folder' or '🎯 Add Game (.exe)' to add any game instantly.",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=C_TEXT_MUTED
            ).pack(pady=4)
            return

        for game in self.filtered_games:
            self._render_single_game_card(game)

    def _render_single_game_card(self, game: DetectedGame):
        """Renders one elevated gaming card"""
        game_prefs = self.state.get_game_pref(game.game_id)
        current_profile = game_prefs.get("profile", "sweet_spot")
        current_res = game_prefs.get("resolution", "1080p")
        db_profile = get_game_profile(game.game_id, game.engine)

        is_hdd = (game.drive_type == "HDD")
        border_col = C_ACCENT_AMBER if is_hdd else C_BORDER

        card = ctk.CTkFrame(
            self.cards_scroll,
            fg_color=C_BG_CARD,
            border_color=border_col,
            border_width=1,
            corner_radius=10
        )
        card.pack(fill="x", pady=8, padx=4)

        # 1. Header Row
        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(14, 8))

        title_lbl = ctk.CTkLabel(
            header_row,
            text=game.name,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=C_TEXT_WHITE
        )
        title_lbl.pack(side="left")

        # Engine Badge
        engine_label = "UE5" if "unreal_engine_5" in game.engine else ("UE4" if "unreal_engine_4" in game.engine else game.engine.replace("_", " ").title())
        engine_badge = ctk.CTkLabel(
            header_row,
            text=f" {engine_label} ",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#0f2638",
            text_color=C_ACCENT_CYAN,
            corner_radius=6
        )
        engine_badge.pack(side="left", padx=8)

        # Drive Badge
        if is_hdd:
            drive_badge = ctk.CTkLabel(
                header_row,
                text=f" ⚠️ HDD [{game.drive_letter}:] Stutter Risk! ",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color="#854d0e",
                text_color="#fef08a",
                corner_radius=6
            )
        else:
            drive_badge = ctk.CTkLabel(
                header_row,
                text=f" ⚡ SSD [{game.drive_letter}:] ",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color="#063820",
                text_color=C_ACCENT_GREEN,
                corner_radius=6
            )
        drive_badge.pack(side="left")

        # Path Snippet
        dir_snippet = game.install_dir
        if len(dir_snippet) > 55:
            dir_snippet = dir_snippet[:22] + "..." + dir_snippet[-28:]
        ctk.CTkLabel(
            header_row,
            text=dir_snippet,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=C_TEXT_MUTED
        ).pack(side="right")

        # 2. Performance & Bottleneck HUD Box
        pred = predict_fps_and_bottleneck(
            hw_specs=self.specs,
            game_requirements=db_profile.get("requirements", {}),
            profile_id=current_profile,
            resolution=current_res,
            drive_type=game.drive_type
        )

        perf_box = ctk.CTkFrame(card, fg_color=C_BG_INNER, corner_radius=8, border_width=1, border_color=C_BORDER)
        perf_box.pack(fill="x", padx=16, pady=(0, 10))

        perf_left = ctk.CTkFrame(perf_box, fg_color="transparent")
        perf_left.pack(side="left", padx=12, pady=8)

        ctk.CTkLabel(
            perf_left,
            text=f"~{pred['avg_fps']} FPS",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=C_ACCENT_GREEN
        ).pack(side="left")

        ctk.CTkLabel(
            perf_left,
            text=f" Avg   |   1% Lows: ~{pred.get('one_percent_low', 0)} FPS",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=C_TEXT_GRAY
        ).pack(side="left", padx=6)

        bn_text = pred.get("bottleneck" if self.state.lang == "en" else "bottleneck_ar", "Balanced")
        bn_color = C_ACCENT_AMBER if "CPU" in pred.get("bottleneck", "") else C_ACCENT_GREEN
        ctk.CTkLabel(
            perf_box,
            text=f"● {bn_text}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=bn_color
        ).pack(side="left", padx=16)

        # Resolution Switcher on Right of Perf Box
        res_frame = ctk.CTkFrame(perf_box, fg_color="transparent")
        res_frame.pack(side="right", padx=12, pady=6)

        ctk.CTkLabel(res_frame, text=t("resolution_label", self.state.lang) + ":", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=C_TEXT_MUTED).pack(side="left", padx=(0, 6))

        res_seg = ctk.CTkSegmentedButton(
            res_frame,
            values=["1080p", "1440p", "4K"],
            command=lambda r, gid=game.game_id: self._update_game_res(gid, r),
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
        )
        res_seg.pack(side="left")
        res_seg.set(current_res)

        # 3. The 7 Holy Presets Segmented Bar
        presets_frame = ctk.CTkFrame(card, fg_color="transparent")
        presets_frame.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            presets_frame,
            text=t("profile_label", self.state.lang) + ":",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=C_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        preset_labels_list = [PRESET_DISPLAY_NAMES[k][self.state.lang] for k in PRESET_KEYS]
        preset_seg = ctk.CTkSegmentedButton(
            presets_frame,
            values=preset_labels_list,
            command=lambda val, gid=game.game_id: self._on_preset_seg_selected(gid, val),
            height=32,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
        )
        preset_seg.pack(fill="x")
        preset_seg.set(PRESET_DISPLAY_NAMES[current_profile][self.state.lang])

        active_pinfo = PROFILES_INFO.get(current_profile, {})
        desc_text = active_pinfo.get(f"desc_{self.state.lang}", active_pinfo.get("desc_en", ""))
        ctk.CTkLabel(
            presets_frame,
            text=f"💡 {desc_text}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=C_TEXT_GRAY
        ).pack(anchor="w", pady=(4, 0))

        # 4. Toggles Row (HDD Savior, DX11, Raw Mouse)
        tweaks_row = ctk.CTkFrame(card, fg_color="transparent")
        tweaks_row.pack(fill="x", padx=16, pady=(4, 8))

        chk_hdd = ctk.CTkCheckBox(
            tweaks_row,
            text=t("hdd_savior_tag", self.state.lang) + (" [Recommended]" if is_hdd else ""),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold" if is_hdd else "normal"),
            text_color=C_ACCENT_AMBER if is_hdd else C_TEXT_WHITE,
            checkbox_height=20,
            checkbox_width=20,
            corner_radius=4,
            command=lambda: self.state.set_game_pref(game.game_id, "hdd_savior", chk_hdd.get() == 1)
        )
        chk_hdd.pack(side="left", padx=(0, 20))
        if game_prefs.get("hdd_savior", is_hdd):
            chk_hdd.select()

        chk_dx11 = ctk.CTkCheckBox(
            tweaks_row,
            text=t("dx11_tag", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=C_TEXT_WHITE,
            checkbox_height=20,
            checkbox_width=20,
            corner_radius=4,
            command=lambda: self.state.set_game_pref(game.game_id, "dx11", chk_dx11.get() == 1)
        )
        chk_dx11.pack(side="left", padx=(0, 20))
        if game_prefs.get("dx11", False):
            chk_dx11.select()

        chk_mouse = ctk.CTkCheckBox(
            tweaks_row,
            text="🎯 Raw 1:1 Mouse Input",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=C_TEXT_WHITE,
            checkbox_height=20,
            checkbox_width=20,
            corner_radius=4,
            command=lambda: self.state.set_game_pref(game.game_id, "raw_mouse", chk_mouse.get() == 1)
        )
        chk_mouse.pack(side="left")
        if game_prefs.get("raw_mouse", True):
            chk_mouse.select()

        # 5. Autonomous Config Hunter Strip
        custom_cfg = game_prefs.get("custom_config_dir")
        hunt_res = find_game_config_autonomously(
            game_id=game.game_id,
            game_name=game.name,
            install_dir=game.install_dir,
            exe_path=game.exe_path,
            engine_hint=game.engine,
            app_id=game.app_id
        )
        active_cfg = custom_cfg or hunt_res.config_dir
        cfg_display = active_cfg
        if len(cfg_display) > 55:
            cfg_display = cfg_display[:22] + "..." + cfg_display[-30:]

        hunter_strip = ctk.CTkFrame(card, fg_color=C_BG_INNER, corner_radius=6, border_width=1, border_color=C_BORDER)
        hunter_strip.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            hunter_strip,
            text="🎯 Config File:",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=C_ACCENT_GREEN
        ).pack(side="left", padx=(10, 4), pady=4)

        ctk.CTkLabel(
            hunter_strip,
            text=f" {cfg_display} ",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#e2e8f0",
            fg_color="#081018",
            corner_radius=4
        ).pack(side="left", padx=4)

        match_tag = f"[{hunt_res.source} • {hunt_res.confidence}% match]" if not custom_cfg else "[Custom Override]"
        ctk.CTkLabel(
            hunter_strip,
            text=match_tag,
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=C_ACCENT_CYAN
        ).pack(side="left", padx=6)

        def on_change_cfg(gid=game.game_id):
            d = filedialog.askdirectory(title=f"Select Config Folder for {game.name}")
            if d:
                self.state.set_game_pref(gid, "custom_config_dir", d)
                self.show_toast(f"Custom config folder set for {game.name}!", "info")
                self.render_game_cards()

        btn_chg = ctk.CTkButton(
            hunter_strip,
            text=t("change_config_btn", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            height=24,
            width=65,
            fg_color="#1e293b",
            hover_color="#334155",
            text_color=C_ACCENT_AMBER,
            corner_radius=4,
            command=on_change_cfg
        )
        btn_chg.pack(side="right", padx=6, pady=4)

        # 6. Action Footer (Apply, Restore, Launch, Open Dir)
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(0, 14))

        apply_btn = ctk.CTkButton(
            footer,
            text=t("apply_profile", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=C_ACCENT_GREEN,
            text_color="#04160e",
            hover_color="#34d399",
            height=36,
            corner_radius=6,
            command=lambda g=game, p=current_profile, h=chk_hdd, d=chk_dx11: self._apply_profile(g, p, h.get() == 1, d.get() == 1)
        )
        apply_btn.pack(side="left", padx=(0, 8))

        restore_btn = ctk.CTkButton(
            footer,
            text=t("restore_backup", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#1e293b",
            text_color=C_TEXT_GRAY,
            hover_color="#334155",
            height=36,
            corner_radius=6,
            command=lambda g=game: self._restore_game(g)
        )
        restore_btn.pack(side="left", padx=(0, 8))

        # Launch Game Button
        launch_btn = ctk.CTkButton(
            footer,
            text=t("launch_game_btn", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#4338ca",
            hover_color="#4f46e5",
            height=36,
            corner_radius=6,
            command=lambda g=game, d=chk_dx11: self._launch_game(g, d.get() == 1)
        )
        launch_btn.pack(side="left", padx=(0, 8))

        open_dir_btn = ctk.CTkButton(
            footer,
            text=t("open_config_btn", self.state.lang),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#0f172a",
            text_color=C_ACCENT_CYAN,
            hover_color="#1e293b",
            height=36,
            corner_radius=6,
            command=lambda g=game: self._open_config_folder(g)
        )
        open_dir_btn.pack(side="right")

    def _on_preset_seg_selected(self, game_id: str, display_val: str):
        for k, v in PRESET_DISPLAY_NAMES.items():
            if v[self.state.lang] == display_val:
                self.state.set_game_pref(game_id, "profile", k)
                break
        self.render_game_cards()

    def _update_game_res(self, game_id: str, resolution: str):
        self.state.set_game_pref(game_id, "resolution", resolution)
        self.render_game_cards()

    def _apply_profile(self, game: DetectedGame, profile_id: str, enable_hdd: bool, force_dx11: bool):
        custom_cfg = self.state.get_game_pref(game.game_id).get("custom_config_dir")
        success, msg = apply_game_profile(
            game_id=game.game_id,
            profile_id=profile_id,
            enable_hdd_savior=enable_hdd,
            force_dx11=force_dx11,
            custom_config_dir=custom_cfg,
            game_name=game.name,
            install_dir=game.install_dir,
            exe_path=game.exe_path,
            engine_hint=game.engine,
            app_id=game.app_id
        )
        if success:
            profile_name = PRESET_DISPLAY_NAMES.get(profile_id, {}).get(self.state.lang, profile_id)
            user_msg = t("success_applied", self.state.lang, profile=profile_name, game=game.name)
            self.show_toast(user_msg, "success")
        else:
            self.show_toast(f"❌ {msg}", "error")

    def _restore_game(self, game: DetectedGame):
        custom_cfg = self.state.get_game_pref(game.game_id).get("custom_config_dir")
        success, msg = restore_game_backup(
            game_id=game.game_id,
            custom_config_dir=custom_cfg,
            game_name=game.name,
            install_dir=game.install_dir,
            exe_path=game.exe_path,
            engine_hint=game.engine,
            app_id=game.app_id
        )
        if success:
            user_msg = t("success_restored", self.state.lang, game=game.name)
            self.show_toast(user_msg, "info")
        else:
            self.show_toast(f"ℹ️ {msg}", "warning")

    def _open_config_folder(self, game: DetectedGame):
        custom_cfg = self.state.get_game_pref(game.game_id).get("custom_config_dir")
        cfg_dir = resolve_game_config_dir(
            game.game_id,
            custom_config_dir=custom_cfg,
            game_name=game.name,
            install_dir=game.install_dir,
            exe_path=game.exe_path,
            engine_hint=game.engine,
            app_id=game.app_id
        )
        if os.path.exists(cfg_dir):
            try:
                subprocess.Popen(f'explorer "{cfg_dir}"')
                self.show_toast(f"Opened: {cfg_dir}", "info")
            except Exception as ex:
                self.show_toast(f"Failed to open directory: {str(ex)}", "error")
        else:
            self.show_toast(f"Directory not found: {cfg_dir}", "warning")

    def _launch_game(self, game: DetectedGame, force_dx11: bool):
        flags = ["-novid", "-high", "-USEALLAVAILABLECORES"]
        if force_dx11:
            flags.append("-dx11")

        if game.exe_path and os.path.exists(game.exe_path):
            ok, msg = launch_game_optimized(game.exe_path, flags)
            self.show_toast(msg, "success" if ok else "error")
        elif game.app_id:
            try:
                os.startfile(f"steam://run/{game.app_id}")
                self.show_toast(f"Launched {game.name} via Steam!", "success")
            except Exception as ex:
                self.show_toast(str(ex), "error")
        else:
            self.show_toast(f"Executable not found for {game.name}", "warning")

    # ==========================================
    # VIEW 2: HARDWARE HUD
    # ==========================================
    def _build_hardware_view(self) -> ctk.CTkFrame:
        view = ctk.CTkScrollableFrame(self.content_container, fg_color=C_BG_ROOT, corner_radius=0)

        ctk.CTkLabel(
            view,
            text="⚡ Hardware Analysis Deck & Bottleneck Inspector",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=C_TEXT_WHITE
        ).pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            view,
            text="Live deep inspection of your GPU, CPU, RAM, and Storage partition topology.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=C_TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # Overall Score Card
        score_card = ctk.CTkFrame(view, fg_color="#0a1e14", corner_radius=10, border_width=1, border_color="#10b981")
        score_card.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(
            score_card,
            text=f"🔥 Overall Gaming Rig Rating: {self.hw_score}/100",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=C_ACCENT_GREEN
        ).pack(anchor="w", padx=16, pady=(12, 4))

        rating_desc = "High-tier gaming rig. Ultra settings capable on 1080p and 1440p high-refresh." if self.hw_score >= 70 else "Balanced gaming system. Sweet-Spot and Tryhard-Pro presets recommended for optimal framepacing."
        ctk.CTkLabel(
            score_card,
            text=rating_desc,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#a7f3d0"
        ).pack(anchor="w", padx=16, pady=(0, 12))

        # Detailed Specs Grid
        gpu = self.specs.get("gpu", {})
        cpu = self.specs.get("cpu", {})
        ram = self.specs.get("ram", {})
        drives = self.specs.get("drives", {})

        def make_spec_card(title, icon, details: List[Tuple[str, str]], accent_col):
            c = ctk.CTkFrame(view, fg_color=C_BG_CARD, corner_radius=10, border_width=1, border_color=C_BORDER)
            c.pack(fill="x", padx=20, pady=8)

            header = ctk.CTkFrame(c, fg_color="transparent")
            header.pack(fill="x", padx=16, pady=(12, 8))
            ctk.CTkLabel(header, text=f"{icon} {title}", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=accent_col).pack(side="left")

            body = ctk.CTkFrame(c, fg_color=C_BG_INNER, corner_radius=6)
            body.pack(fill="x", padx=16, pady=(0, 12))

            for k, v in details:
                row = ctk.CTkFrame(body, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=4)
                ctk.CTkLabel(row, text=f"{k}:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=C_TEXT_MUTED).pack(side="left")
                ctk.CTkLabel(row, text=str(v), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=C_TEXT_WHITE).pack(side="right")

        make_spec_card("Graphics Processing Unit (GPU)", "🎮", [
            ("Model", gpu.get("name", "Unknown")),
            ("Dedicated VRAM", f"{gpu.get('vram_gb', 0):.1f} GB GDDR6"),
            ("Driver Version", gpu.get("driver_version", "Unknown")),
            ("Performance Score", f"{gpu.get('score', 0)}/100")
        ], C_ACCENT_GREEN)

        make_spec_card("Central Processing Unit (CPU)", "⚡", [
            ("Processor", cpu.get("name", "Unknown")),
            ("Topology", f"{cpu.get('physical_cores', 0)} Physical Cores / {cpu.get('logical_cores', 0)} Threads"),
            ("Architecture Score", f"{cpu.get('score', 0)}/100")
        ], C_ACCENT_CYAN)

        make_spec_card("System Memory (RAM)", "🧠", [
            ("Total Memory", f"{ram.get('total_gb', 0):.1f} GB High-Speed"),
            ("Available Free", f"{ram.get('avail_gb', 0):.1f} GB"),
            ("Capacity Rating", f"{ram.get('score', 0)}/100")
        ], "#c084fc")

        drive_items = [(f"Drive {drv}:", f"{mtype} (Stutter Alert Active)" if mtype == "HDD" else f"{mtype} (Ultra Fast)") for drv, mtype in drives.items()]
        make_spec_card("Storage Drive Topology", "💿", drive_items or [("Drives", "C: SSD")], C_ACCENT_AMBER)

        return view

    # ==========================================
    # VIEW 3: STEAM & DLC HUB (GreenLuma Engine)
    # ==========================================
    def _build_steam_hub_view(self) -> ctk.CTkFrame:
        view = ctk.CTkScrollableFrame(self.content_container, fg_color=C_BG_ROOT, corner_radius=0)

        ctk.CTkLabel(
            view,
            text="🔓 Steam & DLC Hub (GreenLuma Integration)",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=C_TEXT_WHITE
        ).pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            view,
            text="Autonomous Steam library manager, AppList generator, and Family Sharing unlock engine.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=C_TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 20))

        steam_path = get_steam_path()
        users = get_steam_users(steam_path)

        # Steam Status Card
        stat_card = ctk.CTkFrame(view, fg_color=C_BG_CARD, corner_radius=10, border_width=1, border_color=C_BORDER)
        stat_card.pack(fill="x", padx=20, pady=(0, 16))

        h = ctk.CTkFrame(stat_card, fg_color="transparent")
        h.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(h, text="Steam Installation Status", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=C_ACCENT_CYAN).pack(side="left")

        body = ctk.CTkFrame(stat_card, fg_color=C_BG_INNER, corner_radius=6)
        body.pack(fill="x", padx=16, pady=(0, 12))

        def add_row(parent, title, val):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(r, text=title, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=C_TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=C_TEXT_WHITE).pack(side="right")

        add_row(body, "Detected Steam Path:", steam_path or "Not Detected")
        add_row(body, "Active Steam Accounts:", ", ".join(users) if users else "None")
        add_row(body, "Target AppList Folder:", os.path.join(steam_path, "AppList") if steam_path else "C:\\AppList")

        # GreenLuma Generator Card
        gen_card = ctk.CTkFrame(view, fg_color=C_BG_CARD, corner_radius=10, border_width=1, border_color=C_BORDER)
        gen_card.pack(fill="x", padx=20, pady=8)

        gh = ctk.CTkFrame(gen_card, fg_color="transparent")
        gh.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(gh, text="🚀 One-Click AppList & Family Sharing Fixer", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=C_ACCENT_GREEN).pack(side="left")

        ctk.CTkLabel(
            gen_card,
            text="Automatically generates continuous numbered files (0.txt, 1.txt...) to fix 'from your steam family library' errors.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=C_TEXT_GRAY
        ).pack(anchor="w", padx=16, pady=(0, 12))

        g_body = ctk.CTkFrame(gen_card, fg_color=C_BG_INNER, corner_radius=6)
        g_body.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(
            g_body,
            text="Enter AppIDs (separated by comma or newline):",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=C_TEXT_WHITE
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.applist_entry = ctk.CTkEntry(
            g_body,
            placeholder_text="e.g. 1808500, 730, 2073850",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=36,
            fg_color="#0c0e14",
            border_color=C_BORDER
        )
        self.applist_entry.pack(fill="x", padx=12, pady=(0, 10))

        # Preset Helper Buttons
        helper_frame = ctk.CTkFrame(g_body, fg_color="transparent")
        helper_frame.pack(fill="x", padx=12, pady=(0, 10))

        def set_preset_appids(appids: str):
            self.applist_entry.delete(0, "end")
            self.applist_entry.insert(0, appids)

        ctk.CTkButton(helper_frame, text="+ ARC Raiders (1808500)", height=26, font=ctk.CTkFont(family="Segoe UI", size=10), fg_color="#1e293b", hover_color="#334155", command=lambda: set_preset_appids("1808500")).pack(side="left", padx=2)
        ctk.CTkButton(helper_frame, text="+ CS2 (730)", height=26, font=ctk.CTkFont(family="Segoe UI", size=10), fg_color="#1e293b", hover_color="#334155", command=lambda: set_preset_appids("730")).pack(side="left", padx=2)
        ctk.CTkButton(helper_frame, text="+ Outlast Trials (1304930)", height=26, font=ctk.CTkFont(family="Segoe UI", size=10), fg_color="#1e293b", hover_color="#334155", command=lambda: set_preset_appids("1304930")).pack(side="left", padx=2)

        def on_generate_applist():
            raw = self.applist_entry.get().strip()
            if not raw:
                self.show_toast("Please enter at least one valid Steam AppID", "warning")
                return

            ids = []
            for item in re.split(r"[,;\s]+", raw):
                if item.isdigit():
                    ids.append(int(item))

            if not ids:
                self.show_toast("No numerical AppIDs found", "error")
                return

            ok, path, count = generate_greenluma_applist(ids)
            if ok:
                self.show_toast(f"Successfully generated {count} AppList files in: {path}", "success")
            else:
                self.show_toast(f"Failed to generate AppList: {path}", "error")

        btn_run_gen = ctk.CTkButton(
            g_body,
            text="🚀 Generate AppList & Fix Family Sharing Now",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=C_ACCENT_GREEN,
            text_color="#04160e",
            hover_color="#34d399",
            height=38,
            command=on_generate_applist
        )
        btn_run_gen.pack(fill="x", padx=12, pady=(0, 12))

        # Utilities Row
        util_row = ctk.CTkFrame(view, fg_color="transparent")
        util_row.pack(fill="x", padx=20, pady=8)

        def open_applist_folder():
            sp = get_steam_path()
            if sp:
                al = os.path.join(sp, "AppList")
                os.makedirs(al, exist_ok=True)
                os.startfile(al)

        ctk.CTkButton(
            util_row,
            text="📂 Open Steam AppList Folder",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#1e293b",
            hover_color="#334155",
            command=open_applist_folder
        ).pack(side="left", padx=4)

        return view

    # ==========================================
    # VIEW 4: SETTINGS
    # ==========================================
    def _build_settings_view(self) -> ctk.CTkFrame:
        view = ctk.CTkScrollableFrame(self.content_container, fg_color=C_BG_ROOT, corner_radius=0)

        ctk.CTkLabel(
            view,
            text="⚙️ Preferences & Suite Settings",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=C_TEXT_WHITE
        ).pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            view,
            text="Customize optimization engines, language, and custom folder registries.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=C_TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # Language Card
        c1 = ctk.CTkFrame(view, fg_color=C_BG_CARD, corner_radius=10, border_width=1, border_color=C_BORDER)
        c1.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(c1, text="Language Selection", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=C_ACCENT_GREEN).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(c1, text="Choose your primary language. English is recommended for competitive gaming.", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=C_TEXT_GRAY).pack(anchor="w", padx=16, pady=(0, 8))

        s_lang = ctk.CTkSegmentedButton(c1, values=["English", "العربية"], command=self._on_language_changed)
        s_lang.pack(anchor="w", padx=16, pady=(0, 14))
        s_lang.set("English" if self.state.lang == "en" else "العربية")

        # Read-Only Lock Guard Card
        c2 = ctk.CTkFrame(view, fg_color=C_BG_CARD, corner_radius=10, border_width=1, border_color=C_BORDER)
        c2.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(c2, text="Windows Read-Only Protection Guard", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=C_ACCENT_CYAN).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(c2, text="Automatically locks patched GameUserSettings.ini & Engine.ini with FileAttributes.ReadOnly to prevent game reset.", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=C_TEXT_GRAY).pack(anchor="w", padx=16, pady=(0, 8))
        chk_ro = ctk.CTkCheckBox(c2, text="Enforce Read-Only attribute lock on all optimizations", font=ctk.CTkFont(family="Segoe UI", size=11))
        chk_ro.pack(anchor="w", padx=16, pady=(0, 14))
        chk_ro.select()

        # Custom Game Folders Card
        c3 = ctk.CTkFrame(view, fg_color=C_BG_CARD, corner_radius=10, border_width=1, border_color=C_BORDER)
        c3.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(c3, text="Custom Scanned Folders", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=C_ACCENT_AMBER).pack(anchor="w", padx=16, pady=(12, 4))
        folders_txt = "\n".join(self.state.custom_folders) if self.state.custom_folders else "No custom folders added yet."
        ctk.CTkLabel(c3, text=folders_txt, font=ctk.CTkFont(family="Consolas", size=10), text_color=C_TEXT_GRAY).pack(anchor="w", padx=16, pady=(0, 10))

        def clear_custom_folders():
            self.state.custom_folders.clear()
            self.state.save()
            self.rescan_games()
            self.show_toast("Cleared all custom folders registry", "info")

        ctk.CTkButton(c3, text="Clear Custom Folders", fg_color="#ef4444", hover_color="#dc2626", height=28, command=clear_custom_folders).pack(anchor="w", padx=16, pady=(0, 14))

        return view

    def _on_language_changed(self, value):
        self.state.lang = "en" if value == "English" else "ar"
        self.state.save()
        self.show_toast(f"Language updated to {value}", "info")
        # Update Nav
        self.nav_buttons["library"].configure(text=f"  {t('nav_library', self.state.lang)}")
        self.nav_buttons["hardware"].configure(text=f"  {t('nav_hardware', self.state.lang)}")
        self.nav_buttons["steam_hub"].configure(text=f"  {t('nav_steam_hub', self.state.lang)}")
        self.nav_buttons["settings"].configure(text=f"  {t('nav_settings', self.state.lang)}")
        self.btn_add_exe.configure(text=t("add_exe_btn", self.state.lang))
        self.btn_add_folder.configure(text=t("scan_folder_btn", self.state.lang))
        self.render_game_cards()

    def show_toast(self, message: str, level: str = "info"):
        """Displays modern floating cyber toast notification"""
        if self.toast_widget:
            try:
                self.toast_widget.destroy()
            except Exception:
                pass

        color_map = {
            "success": (C_ACCENT_GREEN, "#042f1a"),
            "info": (C_ACCENT_CYAN, "#082f49"),
            "warning": (C_ACCENT_AMBER, "#451a03"),
            "error": (C_ACCENT_RED, "#450a0a")
        }
        fg_col, bg_col = color_map.get(level, (C_ACCENT_GREEN, "#042f1a"))

        toast = ctk.CTkFrame(
            self,
            fg_color=bg_col,
            border_color=fg_col,
            border_width=1,
            corner_radius=8
        )
        toast.place(relx=0.5, rely=0.93, anchor="center")
        self.toast_widget = toast

        ctk.CTkLabel(
            toast,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=fg_col
        ).pack(padx=16, pady=8)

        if self.toast_timer:
            self.after_cancel(self.toast_timer)
        self.toast_timer = self.after(3500, self._dismiss_toast)

    def _dismiss_toast(self):
        if self.toast_widget:
            try:
                self.toast_widget.destroy()
                self.toast_widget = None
            except Exception:
                pass

def launch_app():
    app = ZabbathaApp()
    app.mainloop()

if __name__ == "__main__":
    launch_app()
