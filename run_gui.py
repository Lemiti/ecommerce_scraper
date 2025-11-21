#!/usr/bin/env python3
"""
GUI entry point for the E-commerce Scraper
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.interface.gui_interface import run_gui

if __name__ == "__main__":
    run_gui()