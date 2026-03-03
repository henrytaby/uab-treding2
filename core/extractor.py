from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import logging

class BaseExtractor(ABC):
    """
    Abstract base class for all data extractors.
    Enforces a standard interface for extracting data from different sources.
    """
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def fetch_html(self) -> Optional[str]:
        """
        Fetches the HTML content from the target URL.
        """
        try:
            self.logger.info(f"Fetching data from {self.url}")
            # We use a comprehensive set of headers to mimic a real browser,
            # as Yahoo Finance often blocks generic requests or returns 404s.
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching URL {self.url}: {e}")
            return None

    @abstractmethod
    def parse(self, html_content: str) -> Any:
        """
        Parses the HTML content and extracts the desired data.
        Must be implemented by subclasses.
        
        Args:
            html_content (str): The raw HTML string.
            
        Returns:
            Any: Extracted data (e.g., List of dicts, or a single dict).
        """
        pass

    def execute(self) -> Any:
        """
        Main execution flow: Fetch -> Parse -> Return Data.
        """
        html = self.fetch_html()
        if not html:
            self.logger.warning("No HTML content retrieved. Aborting extraction.")
            return None
            
        return self.parse(html)
