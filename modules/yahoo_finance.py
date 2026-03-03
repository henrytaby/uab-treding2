import os
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from core.extractor import BaseExtractor
from core.config import config
import logging

class YahooTrendingExtractor(BaseExtractor):
    """
    Extractor for Yahoo Finance Trending Stocks.
    Target URL: https://finance.yahoo.com/markets/stocks/trending/
    """
    
    def __init__(self):
        super().__init__(name="top-empresas", url="https://finance.yahoo.com/markets/stocks/trending/")
        
    def _extract_text(self, cell, default="--") -> str:
        """Helper to extract clean text from a BeautifulSoup tag, with a fallback."""
        if not cell:
            return default
        # If there's a span inside, try getting its text first as it usually holds the core value
        span = cell.find('span')
        if span:
            return span.get_text(strip=True)
        return cell.get_text(strip=True) or default

    def parse(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parses the Yahoo Finance trending stocks table HTML.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # In the provided snippet, the rows have the class "row" and "yf-1tpeyy7" or a data-testid="data-table-v2-row"
        rows = soup.find_all('tr', {'data-testid': 'data-table-v2-row'})
        
        if not rows:
            self.logger.warning("No rows found. The HTML structure might have changed or Yahoo blocked the request.")
            return []

        data = []
        for row in rows:
            # Helper to quickly select a cell by its data-testid attribute
            def get_cell_text(testid_val):
                cell = row.find('td', {'data-testid-cell': testid_val})
                return self._extract_text(cell)

            # Special case for ticker symbol, as it often has nested spans or divs
            ticker_cell = row.find('td', {'data-testid-cell': 'ticker'})
            # Attempt to find the symbol class directly
            if ticker_cell:
                symbol_elem = ticker_cell.find(class_='symbol')
                symbol = symbol_elem.get_text(strip=True) if symbol_elem else ticker_cell.get_text(strip=True)
            else:
                symbol = "--"

            # Special case for Name, often it's directly inside the td with specific class
            name_cell = row.find('td', {'data-testid-cell': 'companyshortname.raw'})
            name = name_cell.get_text(strip=True) if name_cell else "--"

            try:
                item = {
                    "Symbol": symbol,
                    "Name": name,
                    "Price": get_cell_text("intradayprice"),
                    "Change": get_cell_text("intradaypricechange"),
                    "Change %": get_cell_text("percentchange"),
                    "Volume": get_cell_text("dayvolume"),
                    "Avg Vol(3M)": get_cell_text("avgdailyvol3m"),
                    "Market Cap": get_cell_text("intradaymarketcap"),
                    "P/E Ratio (TTM)": get_cell_text("peratio.lasttwelvemonths"),
                    "52 Wk Change %": get_cell_text("fiftytwowkpercentchange")
                }
                data.append(item)
            except Exception as e:
                self.logger.error(f"Error parsing a row: {e}")
                
        self.logger.info(f"Successfully extracted {len(data)} records.")
        return data

    def execute_with_fallback(self, test_html_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Executes the extraction. If fetching fails (often due to bot protection),
        it falls back to loading a local HTML file if provided.
        """
        html = self.fetch_html()
        
        if not html or "data-testid=\"data-table-v2-row\"" not in html:
            self.logger.warning("Could not fetch valid HTML from live site. Trying fallback if provided.")
            if test_html_path and os.path.exists(test_html_path):
                self.logger.info(f"Using fallback HTML file: {test_html_path}")
                with open(test_html_path, 'r', encoding='utf-8') as f:
                    html = f.read()
            else:
                self.logger.error("No valid HTML and no fallback provided.")
                return []
                
        return self.parse(html)

    def run_deep_scrape(self, test_html_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Executes the basic trending scrape and then enriches the data by scraping each quote individually.
        """
        data = self.execute_with_fallback(test_html_path)
        if not data:
            self.logger.error("No base data extracted. Deep scrape cannot proceed.")
            return []
            
        self.logger.info(f"Initiating deep scrape for {len(data)} items...")
        enriched_data = []
        for item in data:
            symbol = item.get("Symbol")
            if symbol and symbol != "--":
                self.logger.info(f"Fetching deep details for {symbol}...")
                quote_extractor = YahooQuoteExtractor(symbol=symbol)
                details = quote_extractor.execute()
                
                if details:
                    item.update(details)
                
                time.sleep(config.RATE_LIMIT_DELAY)
            enriched_data.append(item)
            
        return enriched_data

class YahooQuoteExtractor(BaseExtractor):
    """
    Secondary Extractor for individual Yahoo Finance Quote pages.
    Target URL: https://finance.yahoo.com/quote/{symbol}/
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(name=f"quote-{symbol}", url=f"https://finance.yahoo.com/quote/{symbol}/")

    def parse(self, html_content: str) -> Dict[str, Any]:
        """
        Parses the Yahoo Finance individual quote page HTML.
        Returns a single dictionary with the detailed metrics.
        Note: The BaseExtractor returns List[Dict], but for individual quotes we adapt to return a single Dict or a list with one item.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # In the provided snippet, the metrics are inside a list with class "yf-6myrf1"
        lists_ul = soup.find_all('ul', class_='yf-6myrf1')
        
        if not lists_ul:
            self.logger.warning(f"No metric lists found for {self.symbol}. The HTML structure might have changed or Yahoo blocked the request.")
            return {}

        details = {}
        for ul in lists_ul:
            list_items = ul.find_all('li')
            for li in list_items:
                label_span = li.find('span', class_='label')
                value_span = li.find('span', class_='value')
                
                if label_span and value_span:
                    label_text = label_span.get_text(strip=True)
                    value_text = value_span.get_text(strip=True)
                    
                    # Prefix columns to avoid clashes with main table if desired, 
                    # but here we keep them direct.
                    details[label_text] = value_text
                    
        self.logger.info(f"Successfully extracted {len(details)} quote details for {self.symbol}.")
        # To comply with BaseExtractor signature, return a list containing the dict.
        # But for ease of use in main.py, returning a dict directly is more practical for joining.
        return details

    def execute(self) -> Dict[str, Any]:
        """
        Overridden execute to return a Dict instead of a List[Dict] for a single entity fetch.
        """
        html = self.fetch_html()
        if not html:
            self.logger.warning(f"No HTML content retrieved for {self.symbol}. Aborting extraction.")
            return {}
            
        return self.parse(html)

