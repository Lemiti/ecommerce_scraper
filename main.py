#!/usr/bin/env python3

import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader

def main():
    logger = setup_logger("main")
    logger.info("Starting E-commerce Scraper...")

    try:
        config = ConfigLoader.load_config()
        logger.info("Configuration loaded successfully.")
        
        logger.info("Scraper core functionality to be implemented")

    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()