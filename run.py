"""
Zabbatha (ظبطها) - Autonomous Game Optimizer & Deep Engine Tuner Pro
2026 Cyber-Obsidian Edition
Main Entrypoint
"""

import sys
import os

# Ensure current working directory is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zabbatha.ui import launch_app

if __name__ == "__main__":
    launch_app()
