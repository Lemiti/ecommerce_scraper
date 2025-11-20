import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logger import setup_logger

class RequestManager:

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger(__name__)
        self.session = self.create_session()

    def _create_session(self) -> requests.Session:

        session = requests.Session()

        retry_strategy = Retry(
            total=self.config.get('retry_attempts', 3),
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["Get", "POST"],
            backoff_factor=1
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update({
            'User-Agent': self.config.get(
                'user_agent',
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        })

        return session
    
    def get(self, url: str, delay: Optional[float] = None) -> Optional[requests.Response]:
        """
        Make a GET request with retries and delay
        """
        if delay is None:
            delay = self.config.get('delay_between_requests', 1.0)
        
        time.sleep(delay)

        try:
            response = self.session.get(url, timeout=self.config.get('timeout', 30))
            response.raise_for_status()
            return response
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
