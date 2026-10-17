"""
Automated Test Suite for Zabbatha (ظبطها)
Covers Hardware Profiling, Scanning, Database Registry, HDD Savior, Patcher, and Estimator.
"""

import os
import shutil
import tempfile
import unittest

from zabbatha.hardware import get_system_specs
from zabbatha.scanner import scan_steam_libraries, scan_custom_folder, DetectedGame
from zabbatha.database import get_game_profile, PROFILES_INFO
from zabbatha.hdd_savior import inject_hdd_savior_to_engine_ini
from zabbatha.patcher import (
    apply_game_profile,
    restore_backup,
    backup_file_if_needed,
    set_file_readonly,
    resolve_game_config_dir
)
from zabbatha.estimator import predict_fps_and_bottleneck
from zabbatha.localization import t
from zabbatha.state import AppState

class TestZabbatha(unittest.TestCase):
    def test_hardware_detection(self):
        specs = get_system_specs()
        self.assertIn("gpu", specs)
        self.assertIn("cpu", specs)
        self.assertIn("ram", specs)
        self.assertIn("drives", specs)
        self.assertGreater(specs["overall_score"], 0)
        self.assertGreater(specs["gpu"]["vram_gb"], 0)
        self.assertGreater(specs["cpu"]["physical_cores"], 0)

    def test_database_profiles(self):
        expected_presets = [
            "cinema_god", "sweet_spot", "tryhard_pro",
            "stable_60", "cold_lap", "batates_pro", "toaster_god"
        ]
        for p in expected_presets:
            self.assertIn(p, PROFILES_INFO)
            self.assertIn("desc_ar", PROFILES_INFO[p])
            self.assertIn("desc_en", PROFILES_INFO[p])

        arc_prof = get_game_profile("arc_raiders")
        self.assertEqual(arc_prof["name"], "ARC Raiders")
        self.assertEqual(arc_prof["engine"], "unreal_engine_5")
        self.assertIn("presets", arc_prof)
        self.assertIn("toaster_god", arc_prof["presets"])

        gen_prof = get_game_profile("unknown_game_xyz", "unreal_engine_5")
        self.assertEqual(gen_prof["id"], "unknown_game_xyz")
        self.assertIn("presets", gen_prof)

    def test_hdd_savior_engine_ini_injection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_ini = os.path.join(tmpdir, "Engine.ini")
            with open(test_ini, "w") as f:
                f.write("[Core.System]\nPaths=../../../Engine/Content\n")

            inject_hdd_savior_to_engine_ini(test_ini)

            with open(test_ini, "r") as f:
                content = f.read()

            self.assertIn("[SystemSettings]", content)
            self.assertIn("r.Streaming.PoolSize=3000", content)
            self.assertIn("s.AsyncLoadingThreadEnabled=1", content)
            self.assertIn("r.CreateShadersOnLoad=1", content)

    def test_patcher_backup_and_readonly_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_file = os.path.join(tmpdir, "GameUserSettings.ini")
            with open(cfg_file, "w") as f:
                f.write("[ScalabilityGroups]\nsg.ResolutionQuality=100\nsg.ViewDistanceQuality=3\n")

            backup_path = backup_file_if_needed(cfg_file)
            self.assertTrue(os.path.exists(backup_path))

            success, msg = apply_game_profile(
                game_id="arc_raiders",
                profile_id="batates_pro",
                enable_hdd_savior=True,
                force_dx11=True,
                custom_config_dir=tmpdir
            )
            self.assertTrue(success)

            with open(cfg_file, "r") as f:
                patched_content = f.read()

            self.assertIn("sg.ResolutionQuality=70", patched_content)
            self.assertIn("bUseD3D12InGame=False", patched_content)

            restore_ok, rest_msg = restore_backup(tmpdir)
            self.assertTrue(restore_ok)

            with open(cfg_file, "r") as f:
                restored_content = f.read()

            self.assertIn("sg.ResolutionQuality=100", restored_content)

    def test_estimator_fps_and_scaling(self):
        dummy_specs = {
            "gpu": {"name": "RX 7600", "score": 72, "vram_gb": 8.0},
            "cpu": {"name": "Ryzen 5 8400F", "score": 80},
            "ram": {"total_gb": 16.0}
        }
        dummy_reqs = {
            "rec_gpu_score": 65,
            "rec_cpu_score": 65
        }

        res_cinema = predict_fps_and_bottleneck(dummy_specs, dummy_reqs, profile_id="cinema_god", resolution="1080p")
        res_toaster = predict_fps_and_bottleneck(dummy_specs, dummy_reqs, profile_id="toaster_god", resolution="1080p")

        self.assertGreater(res_toaster["avg_fps"], res_cinema["avg_fps"])
        self.assertGreater(res_toaster["one_percent_low"], 0)
        self.assertIn("bottleneck_ar", res_cinema)

    def test_localization_dictionary(self):
        self.assertEqual(t("scan_folder_btn", "ar"), "+ إضافة مجلد ألعاب")
        self.assertEqual(t("scan_folder_btn", "en"), "+ Add Games Folder")
        self.assertIn("ظبطها", t("app_title", "ar"))

    def test_custom_folder_scanner(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            game_dir = os.path.join(tmpdir, "MockGame")
            os.makedirs(game_dir)
            exe_file = os.path.join(game_dir, "MockGame.exe")
            with open(exe_file, "w") as f:
                f.write("mock binary")

            detected = scan_custom_folder(tmpdir)
            self.assertEqual(len(detected), 1)
            self.assertEqual(detected[0].name, "Mockgame")
            self.assertTrue(os.path.exists(detected[0].exe_path))

    def test_smart_config_hunter(self):
        from zabbatha.hunter import find_game_config_autonomously
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test fallback discovery
            res = find_game_config_autonomously("sample_game", "Sample Game", install_dir=tmpdir)
            self.assertIsNotNone(res.config_dir)
            self.assertIn("GameUserSettings.ini", res.primary_file)

if __name__ == "__main__":
    unittest.main()

