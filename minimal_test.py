#!/usr/bin/env python3
"""
Minimal test to find where the script fails
"""

import sys
import traceback
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("Step 1: Testing imports...")

try:
    from src.utils.logger import setup_logger
    print("✓ Logger imported")
    
    from src.utils.config_loader import ConfigLoader
    print("✓ ConfigLoader imported")
    
    from src.core.scraper_engine import ScraperEngine
    print("✓ ScraperEngine imported")
    
    from src.exporters.excel_exporter import ExcelExporter
    print("✓ ExcelExporter imported")
    
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

print("Step 2: Testing configuration...")

try:
    config = ConfigLoader.load_config()
    print("✓ Default config loaded")
    
    website_config = ConfigLoader.load_website_config("books_toscrape")
    print("✓ Website config loaded")
    
except Exception as e:
    print(f"✗ Config loading failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("Step 3: Testing scraper initialization...")

try:
    scraper = ScraperEngine(website_config)
    print("✓ Scraper initialized")
    
except Exception as e:
    print(f"✗ Scraper initialization failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("All minimal tests passed! The issue might be in the scraping process itself.")