import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import time

from src.core.data_models import Product
from src.utils.logger import setup_logger

class GoogleSheetsExporter:
    """
    Export product data to Google Sheets
    """
    
    def __init__(self, credentials_file: str = "./configs/credentials.json"):
        self.credentials_file = Path(credentials_file)
        self.logger = setup_logger(__name__)
        self.client = None
        
    def _authenticate(self) -> bool:
        """Authenticate with Google Sheets API"""
        try:
            if not self.credentials_file.exists():
                self.logger.error(f"Credentials file not found: {self.credentials_file}")
                return False
            
            # Define the scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Authenticate
            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            self.logger.info("Successfully authenticated with Google Sheets API")
            return True
            
        except Exception as e:
            self.logger.error(f"Google Sheets authentication failed: {e}")
            return False
    
    def export_products(self, products: List[Product], 
                       spreadsheet_name: str = None,
                       worksheet_name: str = "Products") -> Optional[str]:
        """
        Export products to Google Sheets
        Returns the spreadsheet URL if successful
        """
        if not products:
            self.logger.warning("No products to export")
            return None
        
        # Authenticate
        if not self._authenticate():
            return None
        
        try:
            # Create spreadsheet name with timestamp
            if not spreadsheet_name:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                spreadsheet_name = f"Scraped Products {timestamp}"
            
            # Create or open spreadsheet
            spreadsheet = self._get_or_create_spreadsheet(spreadsheet_name)
            if not spreadsheet:
                return None
            
            # Create or clear worksheet
            worksheet = self._prepare_worksheet(spreadsheet, worksheet_name)
            if not worksheet:
                return None
            
            # Prepare data for export
            headers, rows = self._prepare_data(products)
            
            # Update worksheet in batches to avoid API limits
            self._update_worksheet_batch(worksheet, headers, rows)
            
            # Format the spreadsheet
            self._format_spreadsheet(worksheet, len(headers), len(rows) + 1)
            
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            self.logger.info(f"Successfully exported {len(products)} products to Google Sheets: {spreadsheet_url}")
            
            return spreadsheet_url
            
        except Exception as e:
            self.logger.error(f"Google Sheets export failed: {e}")
            return None
    
    def _get_or_create_spreadsheet(self, name: str):
        """Get existing spreadsheet or create new one"""
        try:
            # Try to open existing spreadsheet
            spreadsheet = self.client.open(name)
            self.logger.info(f"Opened existing spreadsheet: {name}")
        except gspread.SpreadsheetNotFound:
            try:
                # Create new spreadsheet
                folder_id = "1R6Nr9XgueUPnhl3JvlJWYMZvN_az3SB4"  # Google Drive folder ID of shared folder
                spreadsheet = self.client.create(
                    name,
                    folder_id=folder_id
                )
                self.logger.info(f"Created new spreadsheet: {name}")
            except Exception as e:
                self.logger.error(f"Failed to create spreadsheet: {e}")
                return None
        
        return spreadsheet
    
    def _prepare_worksheet(self, spreadsheet, worksheet_name: str):
        """Prepare worksheet for data export"""
        try:
            # Try to get existing worksheet
            worksheet = spreadsheet.worksheet(worksheet_name)
            # Clear existing data
            worksheet.clear()
            self.logger.info(f"Cleared existing worksheet: {worksheet_name}")
        except gspread.WorksheetNotFound:
            try:
                # Create new worksheet
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=1000, 
                    cols=20
                )
                self.logger.info(f"Created new worksheet: {worksheet_name}")
            except Exception as e:
                self.logger.error(f"Failed to create worksheet: {e}")
                return None
        
        return worksheet
    
    def _prepare_data(self, products: List[Product]):
        """Prepare data for Google Sheets export"""
        if not products:
            return [], []
        
        # Convert products to dictionaries
        product_dicts = [product.to_dict() for product in products]
        
        # Get headers from first product
        headers = list(product_dicts[0].keys())
        
        # Prepare rows
        rows = [headers]  # Header row
        for product in product_dicts:
            row = [product.get(header, '') for header in headers]
            rows.append(row)
        
        return headers, rows
    
    def _update_worksheet_batch(self, worksheet, headers: List[str], rows: List[List]):
        """Update worksheet data in batches to avoid API limits"""
        try:
            # Update in larger batches for better performance
            batch_size = 50
            
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                
                # Calculate range
                start_row = i + 1
                end_row = i + len(batch)
                range_str = f"A{start_row}:{self._get_column_letter(len(headers))}{end_row}"
                
                # Update batch
                worksheet.update(range_str, batch, value_input_option='USER_ENTERED')
                
                self.logger.debug(f"Updated rows {start_row}-{end_row}")
                
                # Small delay to respect API limits
                if i + batch_size < len(rows):
                    time.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"Batch update failed: {e}")
            raise
    
    def _format_spreadsheet(self, worksheet, num_columns: int, num_rows: int):
        """Apply basic formatting to the spreadsheet"""
        try:
            # Format header row
            worksheet.format("A1:Z1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            })
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, num_columns - 1)
            
            # Freeze header row
            worksheet.freeze(rows=1)
            
            self.logger.debug("Applied spreadsheet formatting")
            
        except Exception as e:
            self.logger.warning(f"Formatting failed (non-critical): {e}")
    
    def _get_column_letter(self, column_index: int) -> str:
        """Convert column index to letter (1 = A, 2 = B, etc.)"""
        result = ""
        while column_index > 0:
            column_index, remainder = divmod(column_index - 1, 26)
            result = chr(65 + remainder) + result
        return result