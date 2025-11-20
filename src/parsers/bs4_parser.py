from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urljoin

from src.core.data_models import Product
from src.utils.logger import setup_logger

class BS4Parser:
    def __init__(self, base_url: str, selectors: dict):
        self.base_url = base_url
        self.selectors = selectors
        self.logger = setup_logger(__name__)

    def parse_product_page(self, html:str, product_url: str) -> Optional[Product]:
        """ Parse product details from HTML content """
        
        try:
            soup = BeautifulSoup(html, 'lxml')

            product_data = {
                'product_url': product_url,
                'product_name': self._extract_text,
                'product_name': self._extract_text(soup, self.selectors.get('name')),
                'price': self._extract_text(soup, self.selectors.get('price')),
                'availability': self._extract_text(soup, self.selectors.get('availability')),
                'description': self._extract_text(soup, self.selectors.get('description')),
                'category': self._extract_text(soup, self.selectors.get('category')),
                'image_url': self._extract_attribute(soup, self.selectors.get('image'), 'src'),
            }
            
            # Create Product object
            product = Product(**product_data)
            
            # Clean up image URL
            if product.image_url and not product.image_url.startswith(('http', '//')):
                product.image_url = urljoin(self.base_url, product.image_url)
            
            self.logger.debug(f"Parsed product: {product.product_name}")
            return product
            
        except Exception as e:
            self.logger.error(f"Failed to parse product page {product_url}: {e}")
            return None
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract text using CSS selector"""
        if not selector:
            return None
        
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None
    
    def _extract_attribute(self, soup: BeautifulSoup, selector: str, attribute: str) -> Optional[str]:
        """Extract attribute value using CSS selector"""
        if not selector:
            return None
        
        element = soup.select_one(selector)
        return element.get(attribute) if element else None
    
    def extract_product_links(self, html: str) -> List[str]:
        """
        Extract all product links from a listing page
        """
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        selector = self.selectors.get('product_links')
        if not selector:
            self.logger.warning("No product_links selector configured")
            return links
        
        for link_element in soup.select(selector):
            href = link_element.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                links.append(full_url)
        
        self.logger.info(f"Found {len(links)} product links")
        return links