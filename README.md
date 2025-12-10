# 🚀 E-commerce Product Scraper

A professional, configurable Python-based web scraper for extracting product data from e-commerce websites. Built for freelancers and businesses needing reliable data extraction.

## ✨ **Features**

### **Core Functionality**
- ✅ **Multi-page catalog scraping** with automatic pagination detection
- ✅ **Product data extraction**: name, price, description, images, variants, etc.
- ✅ **Error resilience**: Continues on individual product failures
- ✅ **Rate limiting**: Respectful scraping with configurable delays
- ✅ **Resume capability**: Save/load progress for large catalogs

### **Export Options**
- 📊 **Excel Export**: Clean, formatted `.xlsx` files with timestamps
- ☁️ **Google Sheets Export**: Live cloud-based spreadsheets (API setup required)
- 🖼️ **Image Downloader**: Automatic image downloading with compression
- 📁 **Multiple Formats**: CSV, JSON coming soon

### **User Interfaces**
- 🖥️ **Simple GUI**: Tkinter-based interface for non-technical users
- 💻 **CLI Interface**: Command-line for automation and scripting
- ⚙️ **Configuration System**: JSON-based site configurations

### **Professional Features**
- 🔒 **Compliance-aware**: Respects robots.txt and rate limits
- 📝 **Comprehensive logging**: Detailed logs for debugging
- 🧪 **Unit tests**: Core functionality tested
- 🏗️ **Modular architecture**: Easy to extend and maintain

## 🛠️ **Installation**

### **1. Clone & Setup**
```bash
git clone https://github.com/yourusername/ecommerce-scraper.git
cd ecommerce-scraper
```
#### Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
#### Install dependencies
```bash
pip install -r requirements.txt
```
### **2. Quick Start**

```bash
python main.py

# Run in CLI mode
python main.py --cli

# Run GUI directly
python run_gui.py
```
## 📁 **Project Structure**
```text
ecommerce_scraper/
├── src/                          # Source code
│   ├── core/                     # Core scraping engine
│   │   ├── scraper_engine.py     # Main scraping logic
│   │   └── data_models.py        # Product data models
│   ├── parsers/                  # HTML parsing
│   │   └── bs4_parser.py         # BeautifulSoup parser
│   ├── exporters/                # Data export modules
│   │   ├── excel_exporter.py     # Excel export
│   │   ├── google_sheets_exporter.py  # Google Sheets export
│   │   └── image_downloader.py   # Image downloading
│   ├── utils/                    # Utilities
│   │   ├── request_manager.py    HTTP requests with retry logic
│   │   ├── config_loader.py      # Configuration management
│   │   └── logger.py             # Logging setup
│   └── interface/                # User interfaces
│       ├── gui_interface.py      # Tkinter GUI
│       └── cli_interface.py      # Command-line interface
├── configs/                      # Configuration files
│   ├── default.json              # Default settings
│   └── website_templates/        # Site-specific configurations
├── exports/                      # Output directory (auto-created)
│   ├── products_*.xlsx           # Excel exports
│   └── images/                   # Downloaded images
├── logs/                         # Log files (auto-created)
├── tests/                        # Unit tests
├── main.py                       # Main entry point
├── run_gui.py                    # GUI entry point
└── requirements.txt              # Python dependencies
```
