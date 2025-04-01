import argparse
from core.amazon_scraper import AmazonScraper
from utils.storage import DataStorage

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Amazon Product Scraper')
    
    # Define arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--query', type=str, help='Search query for products')
    group.add_argument('--url', type=str, help='Specific product URL to scrape')
    
    parser.add_argument('--output', type=str, choices=['csv', 'excel', 'sqlite'], 
                      default='csv', help='Output format (default: csv)')
    parser.add_argument('--filename', type=str, default='output', 
                      help='Output filename without extension (default: output)')
    parser.add_argument('--selenium', action='store_true', 
                      help='Use Selenium instead of requests')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = AmazonScraper(use_selenium=args.selenium)
    
    # Get data
    if args.query:
        print(f"Searching for: {args.query}")
        data = scraper.search_products(args.query)
    else:
        print(f"Scraping product page: {args.url}")
        data = [scraper.parse_product_page(args.url)] if args.url else []
    
    # Save data
    if data:
        if args.output == 'csv':
            filename = f"{args.filename}.csv"
            success = DataStorage.save_to_csv(data, filename)
        elif args.output == 'excel':
            filename = f"{args.filename}.xlsx"
            success = DataStorage.save_to_excel(data, filename)
        else:
            filename = f"{args.filename}.db"
            success = DataStorage.save_to_sqlite(data, filename)
        
        if success:
            print(f"Successfully saved {len(data)} items to {filename}")
        else:
            print("Failed to save data")
    else:
        print("No data found")

if __name__ == "__main__":
    main()