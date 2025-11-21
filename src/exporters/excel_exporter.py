import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from src.core.data_models import Product
from src.utils.logger import setup_logger

class ExcelExporter:
    """ Export product data to Excel format"""

    def __init__(self, output_path: str="./exports"):
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
        self.logger = setup_logger(__name__)

    def export_products(self, products: List[Product], filename: str = None) -> str:
        """
        Export list of products to Excel file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products_{timestamp}.xlsx"
        
        file_path = self.output_path / filename
        
        try:
            # Convert products to dictionaries
            product_dicts = [product.to_dict() for product in products]
            
            # Create DataFrame and export
            df = pd.DataFrame(product_dicts)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            self.logger.info(f"Successfully exported {len(products)} products to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export to Excel: {e}")
            raise
