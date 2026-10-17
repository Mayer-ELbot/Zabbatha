"""
Cyber-Obsidian Desktop UI for Zabbatha (2026 Edition)
Native Tkinter + Canvas responsive cards, zero-AI-slop styling, high-DPI aware.
"""

import os
import sys
import subprocess
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Dict, Any, Optional

from .hardware import get_system_specs
from .scanner import scan_all_games, scan_custom_folder, DetectedGame
from .database import get_game_profile, PROFILES_INFO
from .patcher import apply_game_profile, restore_game_backup, resolve_game_config_dir
from .hunter import find_game_config_autonomously
from .estimator import predict_fps_and_bottleneck
from .localization import t, STRINGS
from .state import AppState

# High DPI Awareness on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# 2026 Cyber-Obsidian Theme Constants
THEME = {
    "bg_root": "#080b10",
    "bg_header": "#0d131d",
    "bg_hud": "#111827",
    "bg_card": "#131b2a",
    "bg_card_hover": "#172236",
    "bg_card_inner": "#0f1622",
    "border_normal": "#1f2c42",
    "border_focus": "#00f59b",
    "border_hdd": "#f59e0b",
    "accent_mint": "#00f59b",
    "accent_cyan": "#00d2ff",
    "accent_amber": "#f59e0b",
    "accent_purple": "#a855f7",
    "accent_red": "#ef4444",
    "accent_blue": "#3b82f6",
    "text_white": "#ffffff",
    "text_gray": "#94a3b8",
    "text_muted": "#64748b",
    "btn_primary_bg": "#00f59b",
    "btn_primary_fg": "#04160e",
    "btn_sec_bg": "#1e293b",
    "btn_sec_fg": "#cbd5e1",
    "pill_inactive_bg": "#172033",
    "pill_inactive_fg": "#94a3b8",
    "pill_active_bg": "#00f59b",
    "pill_active_fg": "#04160e",
}

PRESET_KEYS = [
    "cinema_god",
    "sweet_spot",
    "tryhard_pro",
    "stable_60",
    "cold_lap",
    "batates_pro",
    "toaster_god"
]

PRESET_LABELS = {
    "cinema_god": {"en": "🎬 Cinema-God", "ar": "🎬 Cinema-God"},
    "sweet_spot": {"en": "⚖️ Sweet-Spot", "ar": "⚖️ Sweet-Spot"},
    "tryhard_pro": {"en": "🏆 Tryhard-Pro", "ar": "🏆 Tryhard-Pro"},
    "stable_60": {"en": "🔒 Stable-60", "ar": "🔒 Stable-60"},
    "cold_lap": {"en": "❄️ Cold-Lap", "ar": "❄️ Cold-Lap"},
    "batates_pro": {"en": "🥔 Batates-Pro", "ar": "🥔 بطاطس Pro"},
    "toaster_god": {"en": "🚀 Toaster-God", "ar": "🚀 خوارق البطاطس"}
}

class ZabbathaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Zabbatha (ظبطها) - Autonomous Game Optimizer Pro 2026")
        self.geometry("1160x840")
        self.minsize(1020, 700)
        self.configure(bg=THEME["bg_root"])

        # State & Specs
        self.state = AppState()
        self.specs = get_system_specs()
        self.hw_score = self.specs.get("overall_score", 70)
        self.games: List[DetectedGame] = []
        self.filtered_games: List[DetectedGame] = []

        # Filter states
        self.search_query = ""
        self.active_filter = "all" # "all", "hdd", "unreal"

        # Toast manager
        self.toast_widget: Optional[tk.Widget] = None
        self.toast_timer = None

        # Build UI Architecture
        self._setup_styles()
        self._build_header()
        self._build_control_bar()
        self._build_cards_container()
        self._build_status_bar()

        # Initial Scan
        self.rescan_games()

    def _setup_styles(self):
        # Configure standard ttk styles for dark scrollbar
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Vertical.TScrollbar",
            background=THEME["bg_header"],
            troughcolor=THEME["bg_root"],
            bordercolor=THEME["border_normal"],
            arrowcolor=THEME["accent_mint"],
            relief="flat"
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", THEME["border_normal"]), ("pressed", THEME["accent_mint"])]
        )

    def _build_header(self):
        """Top Cyber Header & Hardware HUD"""
        self.header_frame = tk.Frame(self, bg=THEME["bg_header"], padx=20, pady=12)
        self.header_frame.pack(fill="x", side="top")

        # Top row: Brand & Language Toggle
        top_row = tk.Frame(self.header_frame, bg=THEME["bg_header"])
        top_row.pack(fill="x")

        # Logo & App Title
        brand_frame = tk.Frame(top_row, bg=THEME["bg_header"])
        brand_frame.pack(side="left")

        title_lbl = tk.Label(
            brand_frame,
            text="⚡ ZABBATHA | ظَبَّطْهَا",
            font=("Segoe UI", 16, "bold"),
            fg=THEME["accent_mint"],
            bg=THEME["bg_header"]
        )
        title_lbl.pack(side="left")

        ver_badge = tk.Label(
            brand_frame,
            text=" v2.0 PRO ",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["accent_cyan"],
            bg="#0e2238",
            relief="flat",
            padx=6,
            pady=2
        )
        ver_badge.pack(side="left", padx=10)

        self.subtitle_lbl = tk.Label(
            brand_frame,
            text=t("app_subtitle", self.state.lang),
            font=("Segoe UI", 9),
            fg=THEME["text_gray"],
            bg=THEME["bg_header"]
        )
        self.subtitle_lbl.pack(side="left", padx=6)

        # Right side controls: Language Button
        lang_btn = tk.Button(
            top_row,
            text="🌐 " + ("English" if self.state.lang == "ar" else "العربية"),
            font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_sec_bg"],
            fg=THEME["text_white"],
            activebackground=THEME["border_normal"],
            activeforeground=THEME["accent_mint"],
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.toggle_language
        )
        lang_btn.pack(side="right")
        self.lang_btn = lang_btn

        # Hardware HUD Panel (Live Chips)
        hud_frame = tk.Frame(self.header_frame, bg=THEME["bg_hud"], padx=12, pady=8, highlightthickness=1, highlightbackground=THEME["border_normal"])
        hud_frame.pack(fill="x", pady=(10, 0))

        gpu_name = self.specs["gpu"]["name"]
        gpu_vram = self.specs["gpu"]["vram_gb"]
        cpu_name = self.specs["cpu"]["name"]
        ram_gb = self.specs["ram"]["total_gb"]
        drives = self.specs.get("drives", {})

        # Chip builder helper
        def make_chip(parent, icon, title, val, color):
            f = tk.Frame(parent, bg=THEME["bg_hud"])
            f.pack(side="left", padx=(0, 20))
            tk.Label(f, text=f"{icon} {title}:", font=("Segoe UI", 8, "bold"), fg=THEME["text_muted"], bg=THEME["bg_hud"]).pack(anchor="w")
            tk.Label(f, text=val, font=("Segoe UI", 9, "bold"), fg=color, bg=THEME["bg_hud"]).pack(anchor="w")

        make_chip(hud_frame, "🎮", "GPU", f"{gpu_name} ({gpu_vram:.0f}GB VRAM)", THEME["accent_mint"])
        make_chip(hud_frame, "⚡", "CPU", cpu_name, THEME["accent_cyan"])
        make_chip(hud_frame, "🧠", "RAM", f"{ram_gb:.0f} GB High-Speed", THEME["text_white"])

        drives_str = " | ".join([f"{k}: {v}" for k, v in drives.items() if v != "Unknown"])
        make_chip(hud_frame, "💿", "Drives", drives_str or "C: SSD", THEME["accent_amber"])

        # Score Gauge on Right
        score_frame = tk.Frame(hud_frame, bg="#0d2319", padx=12, pady=4, highlightthickness=1, highlightbackground=THEME["accent_mint"])
        score_frame.pack(side="right")
        tk.Label(
            score_frame,
            text=f"🔥 Rig Score: {self.hw_score}/100",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["accent_mint"],
            bg="#0d2319"
        ).pack()

    def _build_control_bar(self):
        """Action Buttons, Folder Picker & Live Search Filter"""
        ctrl_frame = tk.Frame(self, bg=THEME["bg_root"], padx=20, pady=12)
        ctrl_frame.pack(fill="x")

        # Search Bar
        search_box = tk.Frame(ctrl_frame, bg=THEME["bg_hud"], highlightthickness=1, highlightbackground=THEME["border_normal"], padx=8, pady=4)
        search_box.pack(side="left", fill="x", expand=True)

        tk.Label(search_box, text="🔍", font=("Segoe UI", 10), fg=THEME["text_muted"], bg=THEME["bg_hud"]).pack(side="left", padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)

        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            bg=THEME["bg_hud"],
            fg=THEME["text_white"],
            insertbackground=THEME["accent_mint"],
            relief="flat"
        )
        self.search_entry.pack(side="left", fill="x", expand=True)

        # Filter Pills: [ All ] [ ⚠️ HDD Games ] [ ⚡ Unreal Engine ]
        filter_box = tk.Frame(ctrl_frame, bg=THEME["bg_root"])
        filter_box.pack(side="left", padx=15)

        self.btn_filter_all = tk.Button(
            filter_box, text="All / الكل", font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_mint"], fg=THEME["btn_primary_fg"], relief="flat", padx=10, pady=4, cursor="hand2",
            command=lambda: self.set_filter("all")
        )
        self.btn_filter_all.pack(side="left", padx=2)

        self.btn_filter_hdd = tk.Button(
            filter_box, text="⚠️ HDD Games", font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_sec_bg"], fg=THEME["accent_amber"], relief="flat", padx=10, pady=4, cursor="hand2",
            command=lambda: self.set_filter("hdd")
        )
        self.btn_filter_hdd.pack(side="left", padx=2)

        self.btn_filter_ue = tk.Button(
            filter_box, text="⚡ Unreal Engine", font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_sec_bg"], fg=THEME["accent_cyan"], relief="flat", padx=10, pady=4, cursor="hand2",
            command=lambda: self.set_filter("unreal")
        )
        self.btn_filter_ue.pack(side="left", padx=2)

        # Primary Action Buttons: Add Custom Games Folder & Rescan
        actions_box = tk.Frame(ctrl_frame, bg=THEME["bg_root"])
        actions_box.pack(side="right")

        self.add_exe_btn = tk.Button(
            actions_box,
            text=t("add_exe_btn", self.state.lang),
            font=("Segoe UI", 9, "bold"),
            bg="#312e81",
            fg="#c7d2fe",
            activebackground="#4338ca",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.pick_and_add_exe
        )
        self.add_exe_btn.pack(side="left", padx=5)

        self.add_folder_btn = tk.Button(
            actions_box,
            text=t("scan_folder_btn", self.state.lang),
            font=("Segoe UI", 9, "bold"),
            bg="#1e3a8a",
            fg="#93c5fd",
            activebackground="#2563eb",
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.pick_and_scan_folder
        )
        self.add_folder_btn.pack(side="left", padx=5)

        self.rescan_btn = tk.Button(
            actions_box,
            text=t("rescan_btn", self.state.lang),
            font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_sec_bg"],
            fg=THEME["text_white"],
            activebackground=THEME["border_normal"],
            activeforeground=THEME["accent_mint"],
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.rescan_games
        )
        self.rescan_btn.pack(side="left", padx=5)

    def _build_cards_container(self):
        """Scrollable Canvas for Game Cards Deck"""
        self.container_frame = tk.Frame(self, bg=THEME["bg_root"], padx=20, pady=0)
        self.container_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.container_frame,
            bg=THEME["bg_root"],
            highlightthickness=0,
            borderwidth=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.container_frame,
            orient="vertical",
            command=self.canvas.yview,
            style="Vertical.TScrollbar"
        )
        self.cards_inner = tk.Frame(self.canvas, bg=THEME["bg_root"])

        self.cards_inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_inner, anchor="nw")
        self.canvas.configure(xscrollincrement="1", yscrollincrement="1", yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Responsive card resizing on window resize
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        # Smooth MouseWheel scrolling
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _build_status_bar(self):
        """Bottom Status & Info Strip"""
        self.status_bar = tk.Frame(self, bg=THEME["bg_header"], padx=20, pady=6)
        self.status_bar.pack(fill="x", side="bottom")

        self.status_lbl = tk.Label(
            self.status_bar,
            text="Ready. Select an optimization preset and click 'Zabbatly (Apply)' to unlock peak FPS.",
            font=("Segoe UI", 9),
            fg=THEME["text_muted"],
            bg=THEME["bg_header"]
        )
        self.status_lbl.pack(side="left")

        self.count_lbl = tk.Label(
            self.status_bar,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["accent_mint"],
            bg=THEME["bg_header"]
        )
        self.count_lbl.pack(side="right")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_language(self):
        self.state.lang = "en" if self.state.lang == "ar" else "ar"
        self.state.save()
        self.lang_btn.configure(text="🌐 " + ("English" if self.state.lang == "ar" else "العربية"))
        self.subtitle_lbl.configure(text=t("app_subtitle", self.state.lang))
        self.add_exe_btn.configure(text=t("add_exe_btn", self.state.lang))
        self.add_folder_btn.configure(text=t("scan_folder_btn", self.state.lang))
        self.rescan_btn.configure(text=t("rescan_btn", self.state.lang))
        self.render_game_cards()
        self.show_toast(f"Language changed to {'العربية' if self.state.lang == 'ar' else 'English'}", "info")

    def set_filter(self, filter_type: str):
        self.active_filter = filter_type

        # Update button highlights
        self.btn_filter_all.configure(
            bg=THEME["accent_mint"] if filter_type == "all" else THEME["btn_sec_bg"],
            fg=THEME["btn_primary_fg"] if filter_type == "all" else THEME["text_white"]
        )
        self.btn_filter_hdd.configure(
            bg=THEME["accent_amber"] if filter_type == "hdd" else THEME["btn_sec_bg"],
            fg=THEME["btn_primary_fg"] if filter_type == "hdd" else THEME["accent_amber"]
        )
        self.btn_filter_ue.configure(
            bg=THEME["accent_cyan"] if filter_type == "unreal" else THEME["btn_sec_bg"],
            fg=THEME["btn_primary_fg"] if filter_type == "unreal" else THEME["accent_cyan"]
        )
        self._filter_and_render()

    def _on_search_changed(self, *args):
        self.search_query = self.search_var.get().strip().lower()
        self._filter_and_render()

    def _filter_and_render(self):
        filtered = []
        for g in self.games:
            # Query match
            if self.search_query:
                match_name = self.search_query in g.name.lower()
                match_engine = self.search_query in g.engine.lower()
                match_dir = self.search_query in g.install_dir.lower()
                if not (match_name or match_engine or match_dir):
                    continue

            # Tag filter match
            if self.active_filter == "hdd" and g.drive_type != "HDD":
                continue
            if self.active_filter == "unreal" and "unreal" not in g.engine.lower():
                continue

            filtered.append(g)

        self.filtered_games = filtered
    def pick_and_add_exe(self):
        """Allows user to point to any game executable directly."""
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

        # Prepend to games list
        self.games = [g for g in self.games if g.game_id != slug]
        self.games.insert(0, game_obj)
        self.state.add_custom_folder(install_dir)

        self.search_var.set(game_name)
        self.show_toast(f"Added '{game_name}'! Config auto-detected: {hunt_res.source}", "success")
        self._filter_and_render()

    def pick_and_scan_folder(self):
        """Allows user to select any directory containing games and adds it to the deck."""
        selected_dir = filedialog.askdirectory(title="Select Game or Games Directory (اختر مجلد الألعاب)")
        if not selected_dir:
            return

        self.state.add_custom_folder(selected_dir)
        new_games = scan_custom_folder(selected_dir)

        if not new_games:
            self.show_toast(f"No game binaries found in '{selected_dir}'", "warning")
            return

        # Add to current games list, deduplicating
        existing_ids = {g.game_id for g in self.games}
        added = 0
        for g in new_games:
            if g.game_id not in existing_ids:
                self.games.append(g)
                existing_ids.add(g.game_id)
                added += 1

        self.show_toast(f"Added {added} new game card(s) from '{os.path.basename(selected_dir)}'!", "success")
        self._filter_and_render()

    def rescan_games(self):
        """Full re-indexing of Steam and custom folders"""
        self.games = scan_all_games(self.state.custom_folders)
        self.filtered_games = list(self.games)
        self._filter_and_render()
        self.show_toast(f"Indexed {len(self.games)} games across all libraries.", "info")

    def render_game_cards(self):
        """Renders the deck of interactive cards"""
        # Clear existing cards
        for widget in self.cards_inner.winfo_children():
            widget.destroy()

        total = len(self.games)
        showing = len(self.filtered_games)
        self.count_lbl.configure(text=f"Showing: {showing} / {total} Games")

        if not self.filtered_games:
            empty_frame = tk.Frame(self.cards_inner, bg=THEME["bg_root"], pady=60)
            empty_frame.pack(fill="x")
            tk.Label(
                empty_frame,
                text="🎮 No matching games found.",
                font=("Segoe UI", 14, "bold"),
                fg=THEME["text_gray"],
                bg=THEME["bg_root"]
            ).pack()
            tk.Label(
                empty_frame,
                text="Click '+ Add Games Folder' to point to an installed game directory.",
                font=("Segoe UI", 10),
                fg=THEME["text_muted"],
                bg=THEME["bg_root"]
            ).pack(pady=6)
            return

        for game in self.filtered_games:
            self._render_single_card(game)

    def _render_single_card(self, game: DetectedGame):
        """Renders a single high-polish Cyber-Obsidian game card"""
        game_prefs = self.state.get_game_pref(game.game_id)
        current_profile = game_prefs.get("profile", "sweet_spot")
        current_res = game_prefs.get("resolution", "1080p")
        db_profile = get_game_profile(game.game_id, game.engine)

        # Border color glows amber if game is on HDD
        is_hdd = game.drive_type == "HDD"
        border_col = THEME["border_hdd"] if is_hdd else THEME["border_normal"]

        card = tk.Frame(
            self.cards_inner,
            bg=THEME["bg_card"],
            highlightthickness=1,
            highlightbackground=border_col,
            padx=16,
            pady=14
        )
        card.pack(fill="x", pady=8)

        # Hover effect
        def on_enter(e):
            card.configure(highlightbackground=THEME["border_focus"])
        def on_leave(e):
            card.configure(highlightbackground=THEME["border_hdd"] if is_hdd else THEME["border_normal"])
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        # --- Card Header ---
        header_row = tk.Frame(card, bg=THEME["bg_card"])
        header_row.pack(fill="x")

        # Game Title
        title_lbl = tk.Label(
            header_row,
            text=game.name,
            font=("Segoe UI", 13, "bold"),
            fg=THEME["text_white"],
            bg=THEME["bg_card"]
        )
        title_lbl.pack(side="left")

        # Engine Tag Badge
        engine_label = "UE5" if "unreal_engine_5" in game.engine else ("UE4" if "unreal_engine_4" in game.engine else game.engine.replace("_", " ").title())
        engine_badge = tk.Label(
            header_row,
            text=f" {engine_label} ",
            font=("Segoe UI", 8, "bold"),
            fg=THEME["accent_cyan"],
            bg="#0f2638",
            padx=6,
            pady=1
        )
        engine_badge.pack(side="left", padx=8)

        # Storage Drive Badge
        if is_hdd:
            storage_badge = tk.Label(
                header_row,
                text=f" ⚠️ HDD [{game.drive_letter}:] - High Stutter Risk! ",
                font=("Segoe UI", 8, "bold"),
                fg="#fef08a",
                bg="#854d0e",
                padx=8,
                pady=1
            )
        else:
            storage_badge = tk.Label(
                header_row,
                text=f" ⚡ SSD [{game.drive_letter}:] ",
                font=("Segoe UI", 8, "bold"),
                fg=THEME["accent_mint"],
                bg="#063820",
                padx=6,
                pady=1
            )
        storage_badge.pack(side="left")

        # Install Dir Snippet (truncated)
        dir_snippet = game.install_dir
        if len(dir_snippet) > 55:
            dir_snippet = dir_snippet[:25] + "..." + dir_snippet[-25:]
        path_lbl = tk.Label(
            header_row,
            text=dir_snippet,
            font=("Segoe UI", 8),
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        path_lbl.pack(side="right")

        # --- Performance & Bottleneck Estimation HUD ---
        pred = predict_fps_and_bottleneck(
            hw_specs=self.specs,
            game_requirements=db_profile.get("requirements", {}),
            profile_id=current_profile,
            resolution=current_res,
            drive_type=game.drive_type
        )

        metrics_frame = tk.Frame(card, bg=THEME["bg_card_inner"], padx=12, pady=8, highlightthickness=1, highlightbackground=THEME["border_normal"])
        metrics_frame.pack(fill="x", pady=(10, 10))

        # FPS Chips
        fps_box = tk.Frame(metrics_frame, bg=THEME["bg_card_inner"])
        fps_box.pack(side="left")

        fps_val_lbl = tk.Label(
            fps_box,
            text=f"~{pred['avg_fps']} FPS",
            font=("Segoe UI", 16, "bold"),
            fg=THEME["accent_mint"],
            bg=THEME["bg_card_inner"]
        )
        fps_val_lbl.pack(side="left")

        fps_sub_lbl = tk.Label(
            fps_box,
            text=f" Avg  |  1% Lows: ~{pred.get('one_percent_low', 0)} FPS",
            font=("Segoe UI", 10),
            fg=THEME["text_gray"],
            bg=THEME["bg_card_inner"]
        )
        fps_sub_lbl.pack(side="left", padx=4)

        # Bottleneck Chip
        bn_text = pred.get("bottleneck" if self.state.lang == "en" else "bottleneck_ar", "Balanced")
        bn_color = THEME["accent_amber"] if "CPU" in pred.get("bottleneck", "") else THEME["accent_mint"]
        bn_lbl = tk.Label(
            metrics_frame,
            text=f"● {bn_text}",
            font=("Segoe UI", 9, "bold"),
            fg=bn_color,
            bg=THEME["bg_card_inner"]
        )
        bn_lbl.pack(side="left", padx=16)

        # Resolution Switcher on Right of Metrics
        res_frame = tk.Frame(metrics_frame, bg=THEME["bg_card_inner"])
        res_frame.pack(side="right")

        res_lbl = tk.Label(res_frame, text=t("resolution_label", self.state.lang) + ":", font=("Segoe UI", 8, "bold"), fg=THEME["text_muted"], bg=THEME["bg_card_inner"])
        res_lbl.pack(side="left", padx=(0, 6))

        for r in ["1080p", "1440p", "4K"]:
            is_active_r = (r == current_res)
            r_btn = tk.Button(
                res_frame,
                text=r,
                font=("Segoe UI", 8, "bold" if is_active_r else "normal"),
                bg=THEME["accent_mint"] if is_active_r else THEME["bg_hud"],
                fg=THEME["btn_primary_fg"] if is_active_r else THEME["text_gray"],
                relief="flat",
                padx=6,
                pady=1,
                cursor="hand2",
                command=lambda res=r: self._update_game_res(game.game_id, res)
            )
            r_btn.pack(side="left", padx=2)

        # --- The 7 Optimization Profiles (Pill Selectors) ---
        profiles_frame = tk.Frame(card, bg=THEME["bg_card"])
        profiles_frame.pack(fill="x", pady=(0, 10))

        prof_title = tk.Label(
            profiles_frame,
            text=t("profile_label", self.state.lang) + ":",
            font=("Segoe UI", 8, "bold"),
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        prof_title.pack(anchor="w", pady=(0, 4))

        pills_row = tk.Frame(profiles_frame, bg=THEME["bg_card"])
        pills_row.pack(fill="x")

        for pkey in PRESET_KEYS:
            is_active_p = (pkey == current_profile)
            pinfo = PROFILES_INFO.get(pkey, {})
            label_text = PRESET_LABELS.get(pkey, {}).get(self.state.lang, pkey)

            p_btn = tk.Button(
                pills_row,
                text=label_text,
                font=("Segoe UI", 8, "bold" if is_active_p else "normal"),
                bg=pinfo.get("badge_color", THEME["accent_mint"]) if is_active_p else THEME["pill_inactive_bg"],
                fg="#ffffff" if is_active_p else THEME["pill_inactive_fg"],
                activebackground=THEME["border_focus"],
                activeforeground="#ffffff",
                relief="flat",
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda pk=pkey: self._update_game_profile(game.game_id, pk)
            )
            p_btn.pack(side="left", padx=2, pady=2)

        # Profile Description Callout
        active_pinfo = PROFILES_INFO.get(current_profile, {})
        desc_text = active_pinfo.get(f"desc_{self.state.lang}", active_pinfo.get("desc_en", ""))
        desc_lbl = tk.Label(
            profiles_frame,
            text=f"💡 {desc_text}",
            font=("Segoe UI", 8),
            fg=THEME["text_gray"],
            bg=THEME["bg_card"]
        )
        desc_lbl.pack(anchor="w", pady=(4, 0))

        # --- Deep Tweaks Row (HDD Savior, DX11, Raw Mouse) ---
        tweaks_row = tk.Frame(card, bg=THEME["bg_card"])
        tweaks_row.pack(fill="x", pady=(4, 10))

        # 1. HDD Savior Checkbox
        hdd_var = tk.BooleanVar(value=game_prefs.get("hdd_savior", is_hdd))
        def on_toggle_hdd():
            self.state.set_game_pref(game.game_id, "hdd_savior", hdd_var.get())
        chk_hdd = tk.Checkbutton(
            tweaks_row,
            text=t("hdd_savior_tag", self.state.lang) + (" [Recommended]" if is_hdd else ""),
            variable=hdd_var,
            font=("Segoe UI", 9, "bold" if is_hdd else "normal"),
            fg=THEME["accent_amber"] if is_hdd else THEME["text_white"],
            selectcolor=THEME["bg_hud"],
            bg=THEME["bg_card"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_amber"],
            command=on_toggle_hdd
        )
        chk_hdd.pack(side="left", padx=(0, 16))

        # 2. Force DX11 Checkbox
        dx11_var = tk.BooleanVar(value=game_prefs.get("dx11", False))
        def on_toggle_dx11():
            self.state.set_game_pref(game.game_id, "dx11", dx11_var.get())
        chk_dx11 = tk.Checkbutton(
            tweaks_row,
            text=t("dx11_tag", self.state.lang),
            variable=dx11_var,
            font=("Segoe UI", 9),
            fg=THEME["text_white"],
            selectcolor=THEME["bg_hud"],
            bg=THEME["bg_card"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_cyan"],
            command=on_toggle_dx11
        )
        chk_dx11.pack(side="left", padx=(0, 16))

        # 3. Raw 1:1 Mouse Input
        mouse_var = tk.BooleanVar(value=game_prefs.get("raw_mouse", True))
        def on_toggle_mouse():
            self.state.set_game_pref(game.game_id, "raw_mouse", mouse_var.get())
        chk_mouse = tk.Checkbutton(
            tweaks_row,
            text="🎯 Raw 1:1 Mouse Input",
            variable=mouse_var,
            font=("Segoe UI", 9),
            fg=THEME["text_white"],
            selectcolor=THEME["bg_hud"],
            bg=THEME["bg_card"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["accent_mint"],
            command=on_toggle_mouse
        )
        chk_mouse.pack(side="left")

        # --- Autonomous Config Hunter Strip ---
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
        if len(cfg_display) > 52:
            cfg_display = cfg_display[:22] + "..." + cfg_display[-26:]

        cfg_strip = tk.Frame(card, bg=THEME["bg_card_inner"], padx=10, pady=6, highlightthickness=1, highlightbackground=THEME["border_normal"])
        cfg_strip.pack(fill="x", pady=(0, 10))

        tk.Label(cfg_strip, text="🎯 Config File:", font=("Segoe UI", 8, "bold"), fg=THEME["accent_mint"], bg=THEME["bg_card_inner"]).pack(side="left")
        tk.Label(cfg_strip, text=f" {cfg_display} ", font=("Consolas", 8), fg="#e2e8f0", bg="#081018").pack(side="left", padx=6)
        match_tag = f"[{hunt_res.source} • {hunt_res.confidence}% Match]" if not custom_cfg else "[Custom Override]"
        tk.Label(cfg_strip, text=match_tag, font=("Segoe UI", 7), fg=THEME["accent_cyan"], bg=THEME["bg_card_inner"]).pack(side="left")

        def on_change_cfg(gid=game.game_id):
            d = filedialog.askdirectory(title=f"Select Config Folder for {game.name}")
            if d:
                self.state.set_game_pref(gid, "custom_config_dir", d)
                self.show_toast(f"Custom config folder saved for {game.name}!", "info")
                self.render_game_cards()

        change_btn = tk.Button(cfg_strip, text="✏️ Change", font=("Segoe UI", 7, "bold"), bg=THEME["btn_sec_bg"], fg=THEME["accent_amber"], relief="flat", padx=6, pady=1, cursor="hand2", command=on_change_cfg)
        change_btn.pack(side="right")

        # --- Card Action Footer ---
        footer_row = tk.Frame(card, bg=THEME["bg_card"])
        footer_row.pack(fill="x", pady=(4, 0))

        # Apply Button (Primary Glowing Green)
        apply_btn = tk.Button(
            footer_row,
            text=t("apply_profile", self.state.lang),
            font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_primary_bg"],
            fg=THEME["btn_primary_fg"],
            activebackground="#34d399",
            activeforeground="#04160e",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=lambda g=game, p=current_profile, h=hdd_var, d=dx11_var: self._apply_profile(g, p, h.get(), d.get())
        )
        apply_btn.pack(side="left", padx=(0, 10))

        # Restore Original Backup Button
        restore_btn = tk.Button(
            footer_row,
            text=t("restore_backup", self.state.lang),
            font=("Segoe UI", 9),
            bg=THEME["btn_sec_bg"],
            fg=THEME["text_gray"],
            activebackground=THEME["border_normal"],
            activeforeground=THEME["text_white"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda g=game: self._restore_game(g)
        )
        restore_btn.pack(side="left", padx=(0, 10))

        # Open Config Directory Button
        open_cfg_btn = tk.Button(
            footer_row,
            text="📂 Open Config Dir / فتح مجلد الإعدادات",
            font=("Segoe UI", 8),
            bg="#0f172a",
            fg=THEME["accent_cyan"],
            activebackground="#1e293b",
            activeforeground="#38bdf8",
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda g=game: self._open_config_folder(g)
        )
        open_cfg_btn.pack(side="right")

    def _update_game_profile(self, game_id: str, profile_id: str):
        self.state.set_game_pref(game_id, "profile", profile_id)
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
            profile_name = PRESET_LABELS.get(profile_id, {}).get(self.state.lang, profile_id)
            user_msg = t("success_applied", self.state.lang, profile=profile_name, game=game.name)
            self.show_toast(user_msg, "success")
            self.status_lbl.configure(text=f"Applied {profile_id} to {game.name}. Read-Only locked.", fg=THEME["accent_mint"])
        else:
            self.show_toast(f"❌ {msg}", "error")
            self.status_lbl.configure(text=msg, fg=THEME["accent_red"])

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
            self.status_lbl.configure(text=f"Restored original config for {game.name}.", fg=THEME["accent_cyan"])
        else:
            self.show_toast(f"ℹ️ {msg}", "warning")
            self.status_lbl.configure(text=msg, fg=THEME["text_muted"])

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

    def show_toast(self, message: str, level: str = "info"):
        """Displays modern floating cyber toast notification"""
        if self.toast_widget:
            try:
                self.toast_widget.destroy()
            except Exception:
                pass

        color_map = {
            "success": (THEME["accent_mint"], "#042f1a"),
            "info": (THEME["accent_cyan"], "#082f49"),
            "warning": (THEME["accent_amber"], "#451a03"),
            "error": (THEME["accent_red"], "#450a0a")
        }
        fg_col, bg_col = color_map.get(level, (THEME["accent_mint"], "#042f1a"))

        toast = tk.Frame(
            self,
            bg=bg_col,
            highlightthickness=1,
            highlightbackground=fg_col,
            padx=16,
            pady=10
        )
        toast.place(relx=0.5, rely=0.92, anchor="center")
        self.toast_widget = toast

        tk.Label(
            toast,
            text=message,
            font=("Segoe UI", 10, "bold"),
            fg=fg_col,
            bg=bg_col
        ).pack()

        # Auto-dismiss after 3.8s
        if self.toast_timer:
            self.after_cancel(self.toast_timer)
        self.toast_timer = self.after(3800, self._dismiss_toast)

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
