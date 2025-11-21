from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urljoin

from src.core.data_models import Product
from src.utils.logger import setup_logger

class BS4Parser:
    """
    BeautifulSoup-based HTML parser for product data extraction
    """
    
    def __init__(self, base_url: str, selectors: dict):
        self.base_url = base_url
        self.selectors = selectors
        self.logger = setup_logger(__name__)
    
    def parse_product_page(self, html: str, product_url: str) -> Optional[Product]:
        """
        Parse product details from HTML content with enhanced extraction
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Enhanced data extraction with multiple fallback selectors
            product_data = {
                'product_url': product_url,
                'product_name': self._extract_with_fallbacks(soup, ['name'], [
                    'h1', '.product-title', '.product-name', '[data-testid="product-title"]'
                ]),
                'price': self._extract_with_fallbacks(soup, ['price'], [
                    '.price', '.current-price', '.product-price', '[data-testid="price"]'
                ]),
                'availability': self._extract_availability(soup),
                'description': self._extract_with_fallbacks(soup, ['description'], [
                    '.product-description', '.description', '[itemprop="description"]'
                ]),
                'category': self._extract_with_fallbacks(soup, ['category'], [
                    '.breadcrumb li:last-child', '.category', '[data-testid="breadcrumb-item"]:last-child'
                ]),
                'image_url': self._extract_image(soup),
                'sku': self._extract_sku(soup),
                'rating': self._extract_rating(soup)
            }
            
            # Clean and validate data
            product_data = self._clean_product_data(product_data)
            
            # Create Product object
            product = Product(**product_data)
            
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
    
    def extract_product_links(self, html: str, base_page_url: str = None) -> List[str]:

        soup = BeautifulSoup(html, 'lxml')
        links = []

        selector = self.selectors.get('product_links')
        if not selector:
            self.logger.warning("No product_links selector configured")
            return links

        # Prefer listing page URL when joining; fallback to base_url
        join_base = base_page_url or self.base_url

        for link_element in soup.select(selector):
            href = link_element.get('href')
            if href:
                full_url = urljoin(join_base, href)
                links.append(full_url)

        self.logger.info(f"Found {len(links)} product links")
        return links
    
    def _extract_with_fallbacks(self, soup: BeautifulSoup, config_keys: list, fallback_selectors: list) -> Optional[str]:
        """Extract data using configured selectors first, then fallbacks"""
        # Try configured selectors first
        for key in config_keys:
            selector = self.selectors.get(key)
            if selector:
                result = self._extract_text(soup, selector)
                if result:
                    return result
        
        # Try fallback selectors
        for selector in fallback_selectors:
            result = self._extract_text(soup, selector)
            if result:
                return result
        
        return None
    
    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extract product availability status"""
        # Look for out-of-stock indicators
        out_of_stock_indicators = [
            '.out-of-stock', '.sold-out', '.unavailable', 
            '[data-testid="out-of-stock"]', '.stock-out'
        ]
        
        for selector in out_of_stock_indicators:
            if soup.select_one(selector):
                return "Out of stock"
        
        # Look for in-stock indicators
        in_stock_indicators = [
            '.in-stock', '.available', '[data-testid="in-stock"]',
            '.add-to-cart', '.buy-now'
        ]
        
        for selector in in_stock_indicators:
            if soup.select_one(selector):
                return "In stock"
        
        return "Unknown"
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product image with multiple strategies"""
        # Try configured selector first
        configured_selector = self.selectors.get('image')
        if configured_selector:
            image_url = self._extract_attribute(soup, configured_selector, 'src')
            if image_url:
                return image_url
        
        # Fallback strategies
        fallback_selectors = [
            '.product-image img', '.main-image img', '[data-testid="product-image"]',
            'img[alt*="product"]', 'img[src*="product"]', '.gallery img'
        ]
        
        for selector in fallback_selectors:
            image_url = self._extract_attribute(soup, selector, 'src')
            if image_url and not any(x in image_url.lower() for x in ['logo', 'icon', 'placeholder']):
                return image_url
        
        return None
    def _extract_sku(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product SKU"""
        sku_selectors = [
            '.sku', '[itemprop="sku"]', '.product-sku', '[data-testid="sku"]'
        ]
        
        for selector in sku_selectors:
            sku = self._extract_text(soup, selector)
            if sku:
                return sku.strip()
        
        return None
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product rating"""
        rating_selectors = [
            '.rating', '.review-score', '[itemprop="ratingValue"]',
            '[data-testid="rating"]'
        ]
        
        for selector in rating_selectors:
            rating_text = self._extract_text(soup, selector)
            if rating_text:
                try:
                    # Extract numbers from text like "4.5 out of 5"
                    import re
                    numbers = re.findall(r'\d+\.?\d*', rating_text)
                    if numbers:
                        return float(numbers[0])
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _clean_product_data(self, product_data: dict) -> dict:
        """Clean and normalize product data"""
        cleaned = product_data.copy()
        
        # Clean price
        if cleaned['price']:
            # Remove currency symbols and extra spaces
            import re
            cleaned['price'] = re.sub(r'[^\d.,]', '', cleaned['price']).strip()
        
        # Clean description - remove extra whitespace
        if cleaned['description']:
            cleaned['description'] = ' '.join(cleaned['description'].split())
        
        return cleaned