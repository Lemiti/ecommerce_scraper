import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Optional, Callable
import threading
import time

from src.core.scraper_engine import ScraperEngine
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.image_downloader import ImageDownloader
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger
from src.exporters.google_sheets_exporter import GoogleSheetsExporter


class ScraperGUI:
    """
    Simple GUI for the E-commerce Scraper
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("E-commerce Product Scraper")
        self.root.geometry("800x600")
        
        self.logger = setup_logger("gui")
        self.scraper: Optional[ScraperEngine] = None
        self.is_scraping = False
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Website Selection
        ttk.Label(main_frame, text="Website:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.website_var = tk.StringVar(value="books_toscrape")
        website_combo = ttk.Combobox(main_frame, textvariable=self.website_var, state="readonly")
        website_combo['values'] = self.get_available_websites()
        website_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Custom URL
        ttk.Label(main_frame, text="Custom URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var)
        url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(0, weight=1)


        # Export options
        self.export_excel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Export to Excel", 
                       variable=self.export_excel_var).grid(row=0, column=0, sticky=tk.W)
        
        self.download_images_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Download Images", 
                       variable=self.download_images_var).grid(row=0, column=1, sticky=tk.W)
        
                # Add to the options frame (around line 45)
        self.export_gsheets_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Export to Google Sheets", 
                    variable=self.export_gsheets_var).grid(row=0, column=2, sticky=tk.W)
        
        
        # Max products
        ttk.Label(options_frame, text="Max Products:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_products_var = tk.StringVar(value="100")
        max_spinbox = ttk.Spinbox(options_frame, from_=1, to=10000, 
                                 textvariable=self.max_products_var, width=10)
        max_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", 
                                      command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        main_frame.rowconfigure(4, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to start...")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # Log output
        ttk.Label(progress_frame, text="Log:").grid(row=2, column=0, sticky=tk.W, pady=(10,0))
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, width=80)
        self.log_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Redirect logger to GUI
        self.setup_log_redirect()
        
    def get_available_websites(self):
        """Get list of available website configurations"""
        try:
            config_path = Path("configs/website_templates")
            if config_path.exists():
                return [f.stem for f in config_path.glob("*.json")]
        except Exception as e:
            self.logger.error(f"Error loading website configs: {e}")
        return ["books_toscrape"]
    
    def setup_log_redirect(self):
        """Redirect logger output to GUI text widget"""
        class TextHandler:
            def __init__(self, text_widget):
                self.text_widget = text_widget
            
            def write(self, message):
                self.text_widget.insert(tk.END, message)
                self.text_widget.see(tk.END)
                self.text_widget.update_idletasks()
            
            def flush(self):
                pass
        
        # Create a simple logger that writes to our text widget
        import logging
        handler = logging.StreamHandler(TextHandler(self.log_text))
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        gui_logger = logging.getLogger('gui_scraper')
        gui_logger.addHandler(handler)
        gui_logger.setLevel(logging.INFO)
        
        self.gui_logger = gui_logger
    
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if self.is_scraping:
            return
            
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start scraping in separate thread
        thread = threading.Thread(target=self._scraping_worker)
        thread.daemon = True
        thread.start()
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.gui_logger.info("Scraping stopped by user")
    
    def _scraping_worker(self):
        """Worker function for scraping in background thread"""
        try:
            # Load configuration
            website_name = self.website_var.get()
            website_config = ConfigLoader.load_website_config(website_name)
            
            # Update configuration with GUI settings
            if self.url_var.get():
                website_config['base_url'] = self.url_var.get()
            
            # Initialize scraper
            from src.core.data_models import ScrapingConfig
            scraping_config = ScrapingConfig()
            
            try:
                max_products = int(self.max_products_var.get())
                scraping_config.max_products = max_products
            except ValueError:
                pass
            
            self.scraper = ScraperEngine(website_config, scraping_config)
            
            # Start scraping
            self.gui_logger.info(f"Starting scrape for {website_name}...")
            products = self.scraper.scrape_catalog()
            
            if products and self.is_scraping:
                self.gui_logger.info(f"Successfully scraped {len(products)} products")
                
                # Export to Excel
                if self.export_excel_var.get():
                    exporter = ExcelExporter()
                    output_file = exporter.export_products(products)
                    self.gui_logger.info(f"Exported to: {output_file}")
                
                # Export to Google Sheets
                if self.export_gsheets_var.get() and products and self.is_scraping:
                    try:
                        gsheets_exporter = GoogleSheetsExporter()
                        spreadsheet_url = gsheets_exporter.export_products(products)
                        if spreadsheet_url:
                            self.gui_logger.info(f"Exported to Google Sheets: {spreadsheet_url}")
                        else:
                            self.gui_logger.warning("Google Sheets export failed - check credentials")
                    except Exception as e:
                        self.gui_logger.error(f"Google Sheets export error: {e}")
                        
                                # Download images
                if self.download_images_var.get():
                    image_downloader = ImageDownloader()
                    downloaded_images = image_downloader.download_product_images(products)
                    self.gui_logger.info(f"Downloaded {len(downloaded_images)} images")
                
                messagebox.showinfo("Success", 
                                  f"Scraping completed!\n"
                                  f"Products: {len(products)}\n"
                                  f"File: {output_file if self.export_excel_var.get() else 'N/A'}")
            
            elif not self.is_scraping:
                self.gui_logger.info("Scraping was stopped")
            else:
                self.gui_logger.warning("No products were scraped")
                
        except Exception as e:
            self.gui_logger.error(f"Scraping failed: {e}")
            messagebox.showerror("Error", f"Scraping failed: {e}")
        
        finally:
            self.is_scraping = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_var.set(100)

def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()