#!/usr/bin/env python3
"""
Professional demo showing the scraper's capabilities
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.scraper_engine import ScraperEngine
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.image_downloader import ImageDownloader
from src.utils.config_loader import ConfigLoader

def run_demo():
    """Run a professional demo showing scraper capabilities"""
    print("🚀 E-commerce Scraper Professional Demo")
    print("=" * 50)
    
    demo_sites = [
        ("Books to Scrape", "books_toscrape", 10),
        ("ASOS Fashion", "asos", 5),
        ("Demo E-commerce", "demo_ecommerce", 8)
    ]
    
    all_results = []
    
    for site_name, config_name, max_products in demo_sites:
        print(f"\n📦 Scraping: {site_name}")
        print("-" * 30)
        
        try:
            # Load configuration
            website_config = ConfigLoader.load_website_config(config_name)
            
            # Initialize scraper with demo settings
            from src.core.data_models import ScrapingConfig
            scraping_config = ScrapingConfig()
            scraping_config.max_products = max_products
            scraping_config.delay_between_requests = 2.0
            
            scraper = ScraperEngine(website_config, scraping_config)
            
            # Scrape products
            products = scraper.scrape_catalog()
            
            if products:
                print(f"✅ SUCCESS: Scraped {len(products)} products")
                
                # Show sample
                sample = products[0]
                print(f"   Sample: {sample.product_name}")
                print(f"   Price: {sample.price}")
                
                all_results.extend(products)
            else:
                print(f"❌ No products found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Export combined results
    if all_results:
        print(f"\n📊 Exporting {len(all_results)} total products...")
        
        # Export to Excel
        exporter = ExcelExporter()
        excel_file = exporter.export_products(all_results, "demo_results.xlsx")
        print(f"✅ Excel export: {excel_file}")
        
        # Download images
        image_downloader = ImageDownloader()
        images = image_downloader.download_product_images(all_results)
        print(f"✅ Downloaded {len(images)} product images")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📁 Check the 'exports' folder for results")
        
    return len(all_results) > 0

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)