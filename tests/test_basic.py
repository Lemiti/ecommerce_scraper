import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.core.data_models import Product
from src.parsers.bs4_parser import BS4Parser

def test_product_creation():
    """Test basic product data model"""
    product = Product(
        product_url="http://example.com/product1",
        product_name="Test Product",
        price="$19.99",
        availability="In stock"
    )
    
    assert product.product_name == "Test Product"
    assert product.price == "$19.99"
    print("✓ Product data model test passed")

def test_parser_initialization():
    """Test parser initialization"""
    selectors = {
        'name': 'h1',
        'price': '.price'
    }
    parser = BS4Parser("http://example.com", selectors)
    
    assert parser.base_url == "http://example.com"
    assert parser.selectors == selectors
    print("✓ Parser initialization test passed")

if __name__ == "__main__":
    test_product_creation()
    test_parser_initialization()
    print("All basic tests passed! ✅")