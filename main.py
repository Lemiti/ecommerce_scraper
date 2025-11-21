#!/usr/bin/env python3
"""
Main entry point for the E-commerce Scraper
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.scraper_engine import ScraperEngine
from src.exporters.excel_exporter import ExcelExporter
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger

def main():
    """Main function"""
    logger = setup_logger("main")
    logger.info("Starting E-commerce Scraper...")
    
    try:
        # Load configuration
        config = ConfigLoader.load_config()
        logger.info("Configuration loaded successfully")
        
        # Load website-specific configuration
        website_config = ConfigLoader.load_website_config("books_toscrape")
        logger.info(f"Loaded configuration for: {website_config.get('name')}")
        
        # Initialize scraper
        scraper = ScraperEngine(website_config)
        
        # Start scraping
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