#!/usr/bin/env python3

import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.scraper_engine import ScraperEngine
from src.exporters.excel_exporter import ExcelExporter
from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader

def main():
    logger = setup_logger("main")
    logger.info("Starting E-commerce Scraper...")

    try:
        config = ConfigLoader.load_config()
        logger.info("Configuration loaded successfully.")
        
        logger.info("Scraper core functionality to be implemented")
        website_config = ConfigLoader.load_website_config("books_toscrape")
        logger.info(f"Loaded configuration for: {website_config.get('name')}")

        scraper = ScraperEngine(website_config)

        products = scraper.scrape_catalog()
        
        # Export results
        if products:
            exporter = ExcelExporter()
            output_file = exporter.export_products(products)
            logger.info(f"Successfully exported {len(products)} products to {output_file}")
        else:
            logger.warning("No products were scraped")
        
        # Save progress for potential resumption
        scraper.save_progress()
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()