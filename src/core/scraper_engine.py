import time
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from tqdm import tqdm

from src.core.data_models import Product, ScrapingConfig
from src.utils.request_manager import RequestManager
from src.parsers.bs4_parser import BS4Parser
from src.utils.logger import setup_logger

class ScraperEngine:
    """
    Main scraping engine that coordinates the scraping process
    """
    
    def __init__(self, website_config: Dict[str, Any], scraping_config: Optional[ScrapingConfig] = None):
        self.website_config = website_config
        self.scraping_config = scraping_config or ScrapingConfig()
        self.logger = setup_logger(__name__)
        
        # Initialize components
        self.request_manager = RequestManager({
            'delay_between_requests': self.scraping_config.delay_between_requests,
            'timeout': self.scraping_config.timeout,
            'retry_attempts': self.scraping_config.retry_attempts,
            'user_agent': self.scraping_config.user_agent
        })
        
        self.parser = BS4Parser(
            base_url=website_config.get('base_url', ''),
            selectors=website_config.get('selectors', {})
        )
        
        # State management
        self.scraped_products: List[Product] = []
        self.failed_urls: List[str] = []
        
    def scrape_catalog(self, start_url: Optional[str] = None) -> List[Product]:
        """
        Main method to scrape entire product catalog
        """
        self.logger.info(f"Starting catalog scrape for {self.website_config.get('name', 'unknown site')}")
        
        if not start_url:
            start_url = self.website_config.get('base_url')
        
        try:
            # Get product links from listing pages
            product_urls = self._get_all_product_urls(start_url)
            
            # Scrape individual product pages
            self._scrape_product_pages(product_urls)
            
            self.logger.info(f"Scraping completed. Success: {len(self.scraped_products)}, Failed: {len(self.failed_urls)}")
            return self.scraped_products
            
        except Exception as e:
            self.logger.error(f"Catalog scraping failed: {e}")
            return self.scraped_products
    
    def _get_all_product_urls(self, start_url: str) -> List[str]:
        """
        Extract product URLs from all listing pages
        """
        all_product_urls = []
        page_number = 1
        max_pages = self.website_config.get('pagination', {}).get('max_pages', 10)
        
        self.logger.info(f"Discovering product URLs (max {max_pages} pages)")
        
        while page_number <= max_pages:
            # Build paginated URL
            pagination_pattern = self.website_config.get('pagination', {}).get('pattern', '')
            if pagination_pattern and '{page_number}' in pagination_pattern:
                page_url = start_url + pagination_pattern.format(page_number=page_number)
            else:
                page_url = start_url  # Single page site
            
            self.logger.debug(f"Scraping listing page {page_number}: {page_url}")
            
            # Fetch and parse listing page
            response = self.request_manager.get(page_url)
            if not response:
                self.logger.warning(f"Failed to fetch listing page {page_url}")
                break
            
            # Extract product links
            product_urls = self.parser.extract_product_links(response.text, base_page_url=page_url)
            
            if not product_urls:
                self.logger.info("No more products found, stopping pagination")
                break
            
            # Add to collection, avoiding duplicates
            for url in product_urls:
                if url not in all_product_urls:
                    all_product_urls.append(url)
            
            self.logger.info(f"Page {page_number}: Found {len(product_urls)} products (Total: {len(all_product_urls)})")
            page_number += 1
            
            # Check if we've reached the product limit
            if (self.scraping_config.max_products and 
                len(all_product_urls) >= self.scraping_config.max_products):
                all_product_urls = all_product_urls[:self.scraping_config.max_products]
                self.logger.info(f"Reached maximum product limit: {self.scraping_config.max_products}")
                break
        
        self.logger.info(f"Total product URLs discovered: {len(all_product_urls)}")
        return all_product_urls
    
    def _scrape_product_pages(self, product_urls: List[str]) -> None:
        """
        Scrape individual product pages
        """
        self.logger.info(f"Scraping {len(product_urls)} product pages...")
        
        for url in tqdm(product_urls, desc="Scraping products"):
            try:
                product = self._scrape_single_product(url)
                if product:
                    self.scraped_products.append(product)
                else:
                    self.failed_urls.append(url)
                    
            except Exception as e:
                self.logger.error(f"Unexpected error scraping {url}: {e}")
                self.failed_urls.append(url)
    
    def _scrape_single_product(self, product_url: str) -> Optional[Product]:
        """
        Scrape a single product page
        """
        response = self.request_manager.get(product_url)
        if not response:
            return None
        
        return self.parser.parse_product_page(response.text, product_url)
    
    def save_progress(self, filepath: str = "scraping_progress.json") -> None:
        """
        Save scraping progress to resume later
        """
        progress_data = {
            'scraped_urls': [p.product_url for p in self.scraped_products],
            'failed_urls': self.failed_urls,
            'website_config': self.website_config,
            'timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        self.logger.info(f"Progress saved to {filepath}")
    
    def load_progress(self, filepath: str = "scraping_progress.json") -> List[str]:
        """
        Load scraping progress and return remaining URLs
        """
        try:
            with open(filepath, 'r') as f:
                progress_data = json.load(f)
            
            scraped_urls = set(progress_data.get('scraped_urls', []))
            all_urls = self._get_all_product_urls(self.website_config.get('base_url'))
            
            # Return URLs that haven't been scraped yet
            remaining_urls = [url for url in all_urls if url not in scraped_urls]
            
            self.logger.info(f"Loaded progress. Remaining URLs: {len(remaining_urls)}")
            return remaining_urls
            
        except FileNotFoundError:
            self.logger.warning("Progress file not found, starting fresh")
            return []