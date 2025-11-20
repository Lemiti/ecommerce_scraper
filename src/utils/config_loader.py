import json
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    @staticmethod
    def load_config(config_path: str="configs/default.json") -> Dict[str, Any]:
        """
        Load configuration from a JSON file
        """

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f'Configuration file not found: {config_path}')
        except json.JSONDecoderError as e:
            raise ValueError(f'Invalid JSON in configuration file: {e}')
    @staticmethod
    def load_website_config(website_name: str) -> Dict[str, Any]:
        """Load website-specific configuration"""

        config_path = Path("configs/website_templates") / f"{website_name}.json"
        return ConfigLoader.load_config(str(config_path))
