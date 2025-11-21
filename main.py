#!/usr/bin/env python3
"""
Main entry point for the E-commerce Scraper
Supports both CLI and GUI modes
"""

import sys
import argparse
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def run_cli():
    """Run in command line mode"""
    from src.core.scraper_engine import ScraperEngine
    from src.exporters.excel_exporter import ExcelExporter
    from src.exporters.google_sheets_exporter import GoogleSheetsExporter  # Add this
    from src.exporters.image_downloader import ImageDownloader
    from src.utils.config_loader import ConfigLoader
    from src.utils.logger import setup_logger

    logger = setup_logger("main")
    logger.info("Starting E-commerce Scraper in CLI mode...")
    
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
            # Export to Excel
            exporter = ExcelExporter()
            output_file = exporter.export_products(products)
            logger.info(f"Successfully exported {len(products)} products to {output_file}")
            
            # Export to Google Sheets if enabled
            if config['export']['google_sheets']['enabled']:
                gsheets_exporter = GoogleSheetsExporter()
                spreadsheet_url = gsheets_exporter.export_products(products)
                if spreadsheet_url:
                    logger.info(f"Exported to Google Sheets: {spreadsheet_url}")
                else:
                    logger.warning("Google Sheets export failed - check credentials")
            
            # Download images
            image_downloader = ImageDownloader()
            downloaded_images = image_downloader.download_product_images(products)
            logger.info(f"Downloaded {len(downloaded_images)} product images")
        else:
            logger.warning("No products were scraped")
        
        # Save progress for potential resumption
        scraper.save_progress()
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

def main():
    """Main entry point with mode selection"""
    parser = argparse.ArgumentParser(description='E-commerce Product Scraper')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    
    args = parser.parse_args()
    
    if args.gui or (not args.cli and not args.gui):
        # Default to GUI if no arguments or --gui specified
        from src.interface.gui_interface import run_gui
        run_gui()
    else:
        # Run in CLI mode
        run_cli()

if __name__ == "__main__":
    main()