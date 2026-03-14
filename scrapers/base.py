"""Base scraper class with common utilities."""

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(
        self,
        name: str,
        base_url: str,
        rate_limit: float = 1.0,
        timeout: int = 30
    ):
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retries
        adapter = HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Set common headers
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        self._last_request_time: Optional[float] = None
    
    def _wait_for_rate_limit(self) -> None:
        """Ensure we don't exceed rate limit."""
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
        self._last_request_time = time.time()
    
    def fetch(self, url: str, **kwargs) -> requests.Response:
        """Fetch URL with rate limiting and error handling."""
        full_url = urljoin(self.base_url, url) if not url.startswith('http') else url
        
        self._wait_for_rate_limit()
        
        try:
            logger.info(f"[{self.name}] Fetching: {full_url}")
            response = self.session.get(
                full_url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"[{self.name}] Request failed: {e}")
            raise
    
    @abstractmethod
    def extract(self, response: requests.Response) -> Dict[str, Any]:
        """Extract data from response. Must be implemented by subclasses."""
        pass
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Fetch and extract data from URL."""
        response = self.fetch(url, **kwargs)
        data = self.extract(response)
        logger.info(f"[{self.name}] Extracted {len(data)} items")
        return data
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
