import requests
from pathlib import Path
from typing import List
from urllib.parse import urlparse
import imghdr

from src.core.data_models import Product
from src.utils.logger import setup_logger

class ImageDownloader:
    """Download and manage product images"""
    
    def __init__(self, download_path: str = "./exports/images"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logger(__name__)
    
    def download_product_images(self, products: List[Product]) -> List[str]:
        """Download images for all products"""
        downloaded_paths = []
        
        for product in products:
            if product.image_url:
                image_path = self.download_image(product.image_url, product.product_name)
                if image_path:
                    downloaded_paths.append(image_path)
        
        self.logger.info(f"Downloaded {len(downloaded_paths)} product images")
        return downloaded_paths
    
    def download_image(self, image_url: str, product_name: str) -> str:
        """Download a single image"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                extension = 'jpg'
            elif 'png' in content_type:
                extension = 'png'
            else:
                # Try to detect from content
                extension = imghdr.what(None, response.content) or 'jpg'
            
            # Create safe filename
            safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name[:50]  # Limit length
            filename = f"{safe_name}.{extension}"
            filepath = self.download_path / filename
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.logger.debug(f"Downloaded image: {filename}")
            return str(filepath)
            
        except Exception as e:
            self.logger.warning(f"Failed to download image {image_url}: {e}")
            return None