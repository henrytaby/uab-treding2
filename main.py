import argparse
import logging
import sys
from modules.yahoo_finance import YahooTrendingExtractor
from core.storage import StorageManager

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Web Data Extraction Project - Object Oriented and Scalable")
    
    # Subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # top-empresas command
    top_parser = subparsers.add_parser("top-empresas", help="Extraer el top de empresas de la bolsa de valores (Yahoo Finance)")
    top_parser.add_argument("--format", type=str, choices=["excel", "json"], help="Output format (default from .env)")
    top_parser.add_argument("--test-html", type=str, help="Path to local HTML file to use as fallback if fetching fails")

    # Add future commands here
    # func1_parser = subparsers.add_parser("funcion1", help="Future functionality")
    
    args = parser.parse_args()

    if args.command == "top-empresas":
        logger.info("Starting top-empresas extraction...")
        
        # Initialize Base Extractor
        from modules.yahoo_finance import YahooTrendingExtractor, YahooQuoteExtractor
        import time
        
        extractor = YahooTrendingExtractor()
        
        # Execute with fallback logic for base table
        fallback_path = args.test_html if args.test_html else "datos/test_html.html"
        data = extractor.execute_with_fallback(test_html_path=fallback_path)
        
        if not data:
            logger.error("No base data extracted. Process failed.")
            sys.exit(1)
            
        # Phase 2: Deep Scrape logic
        logger.info(f"Initiating deep scrape for {len(data)} items...")
        enriched_data = []
        for item in data:
            symbol = item.get("Symbol")
            if symbol and symbol != "--":
                logger.info(f"Fetching deep details for {symbol}...")
                quote_extractor = YahooQuoteExtractor(symbol=symbol)
                details = quote_extractor.execute()
                
                # Merge dictionaries
                if details:
                    item.update(details)
                
                # Sleep to prevent bot blocking
                time.sleep(1)
            enriched_data.append(item)
            
        # Initialize Storage Manager
        storage = StorageManager(module_name="top-empresas")
        
        # Save output
        output_format = args.format if args.format else None
        saved_path = storage.save(enriched_data, format_type=output_format)
        
        if saved_path:
            logger.info(f"Extraction completed successfully. File saved at: {saved_path}")
        else:
            logger.error("Extraction completed but failed to save file.")
            sys.exit(1)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
