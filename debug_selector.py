#!/usr/bin/env python3
"""
Debug tool to test CSS selectors on live websites
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.request_manager import RequestManager
from src.parsers.bs4_parser import BS4Parser

def debug_selectors(url: str, selectors: dict):
    """Test selectors on a specific URL"""
    print(f"Testing selectors on: {url}")
    print("=" * 50)
    
    # Create request manager
    config = {
        'delay_between_requests': 2.0,
        'timeout': 30,
        'retry_attempts': 3
    }
    
    manager = RequestManager(config)
    response = manager.get(url)
    
    if not response:
        print("❌ Failed to fetch page")
        return
    
    # Test selectors
    parser = BS4Parser(url, selectors)
    
    print("Testing product links selector:")
    links = parser.extract_product_links(response.text, url)
    print(f"Found {len(links)} links")
    if links:
        print(f"First 3: {links[:3]}")
    
    print("\nTesting individual product page...")
    if links:
        product_response = manager.get(links[0])
        if product_response:
            product = parser.parse_product_page(product_response.text, links[0])
            if product:
                print("✅ Product parsed successfully:")
                print(f"  Name: {product.product_name}")
                print(f"  Price: {product.price}")
                print(f"  Image: {product.image_url}")
            else:
                print("❌ Failed to parse product")

if __name__ == "__main__":
    # Test Best Buy
    bestbuy_selectors = {
        'product_links': ".sku-item .sku-header a",
        'name': "h1.v-fw-regular",
        'price': ".pricing-price .sr-only",
        'image': ".primary-image"
    }
    
    debug_selectors("https://www.bestbuy.com/site/searchpage.jsp?st=laptop", bestbuy_selectors)