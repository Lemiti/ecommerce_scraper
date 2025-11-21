#!/usr/bin/env python3
"""
Test scraper on multiple e-commerce sites
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.scraper_engine import ScraperEngine
from src.utils.config_loader import ConfigLoader

def test_website(website_name: str, test_url: str = None):
    """Test scraper on a specific website"""
    print(f"\n{'='*50}")
    print(f"Testing: {website_name}")
    print(f"{'='*50}")
    
    try:
        # Load website configuration
        website_config = ConfigLoader.load_website_config(website_name)
        
        # Override URL if provided
        if test_url:
            website_config['base_url'] = test_url
        
        # Initialize scraper with limited products for testing
        from src.core.data_models import ScrapingConfig
        scraping_config = ScrapingConfig()
        scraping_config.max_products = 5  # Just test a few products
        
        scraper = ScraperEngine(website_config, scraping_config)
        
        # Start scraping
        products = scraper.scrape_catalog()
        
        print(f"✅ SUCCESS: Scraped {len(products)} products from {website_name}")
        
        # Show sample data
        if products:
            print(f"Sample product: {products[0].product_name}")
            print(f"Price: {products[0].price}")
            print(f"Image: {products[0].image_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {website_name} - {e}")
        return False

def main():
    """Test multiple websites"""
    websites_to_test = [
        "books_toscrape",  # Should work
        "newegg",          # Electronics
        "bestbuy",         # Electronics  
        "asos",            # Fashion
    ]
    
    results = {}
    
    for website in websites_to_test:
        success = test_website(website)
        results[website] = success
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    for website, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{website}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} websites working")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)