from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime



@dataclass
class Product:
    product_url:str
    product_name: str
    price: Optional[str] = None
    availability: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    sku:Optional[str] = None
    #brand:Optional[str] = None
    specifications: Optional[Dict[str, str]] = None
    breadcrumbs: Optional[str] = None
    scraped_timestamp: str = None #datetime.utcnow().isoformat()


    def __post_init__(self):
        if self.scraped_timestamp is None:
            self.scraped_timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_url": self.product_url,
            "product_name": self.product_name,
            "price": self.price,
            "availability": self.availability,
            "description": self.description,
            "rating": self.rating,
            "review_count": self.review_count,
            "category": self.category,
            "image_url": self.image_url,
            "sku": self.sku,
            #"brand": self.brand,
            "specifications": self.specifications,
            "breadcrumbs": self.breadcrumbs,
            "scraped_timestamp": self.scraped_timestamp
        }
    
@dataclass
class ScrapingConfig:
    delay_between_requests: float = 1.0  # seconds
    timeout: int = 30 
    retry_attempts: int = 3
    max_products: Optional[int] = None  # None means no limit
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" # (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    