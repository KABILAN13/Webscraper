from core.scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class AmazonScraper(BaseScraper):
    def __init__(self, use_selenium=False):
        super().__init__(use_selenium=use_selenium)
        self.base_url = "https://www.amazon.com"
    
    def search_products(self, query):
        search_url = f"{self.base_url}/s?k={query.replace(' ', '+')}"
        soup = self.get_page(search_url)
        
        if not soup:
            return []
            
        products = []
        for item in soup.select('[data-component-type="s-search-result"]'):
            try:
                product = {
                    'name': self._safe_extract(item, ['h2 a span', '.a-size-medium']),
                    'price': self._safe_extract(item, ['.a-price-whole', '.a-offscreen']),
                    'rating': self._safe_extract(item, ['span.a-icon-alt'], split=True),
                    'reviews': self._safe_extract(item, ['span.a-size-base']),
                    'url': self._safe_url_extract(item, ['h2 a', 'a.a-link-normal'])
                }
                if product['name'] and product['url']:
                    products.append(product)
            except Exception:
                continue
        return products
    
    def parse_product_page(self, url):
        """Implementation of required abstract method"""
        soup = self.get_page(url)
        if not soup:
            return None
            
        product = {}
        try:
            product['title'] = self._safe_extract(soup, ['#productTitle', '#ebooksProductTitle'])
            
            # Price extraction
            price_whole = soup.select_one('.a-price-whole')
            price_fraction = soup.select_one('.a-price-fraction')
            product['price'] = f"{price_whole.text}.{price_fraction.text}" if price_whole else 'N/A'
            
            # Rating and reviews
            product['rating'] = self._safe_extract(soup, ['span.a-icon-alt'], split=True)
            product['reviews'] = self._safe_extract(soup, ['#acrCustomerReviewText'])
            
            # Description
            product['description'] = '\n'.join([
                p.text.strip() for p in soup.select('#productDescription p') if p.text.strip()
            ])
            
            # Technical details
            details = {}
            for table in soup.select('#productDetails_detailBullets_sections1, #productDetails_techSpec_section_1'):
                for row in table.select('tr'):
                    if row.th and row.td:
                        details[row.th.text.strip()] = row.td.text.strip()
            product['details'] = details
            
        except Exception as e:
            print(f"Error parsing product page: {e}")
            
        return product
    
    # Helper methods
    def _safe_extract(self, element, selectors, split=False):
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                text = found.text.strip()
                return text.split()[0] if split else text
        return 'N/A'
    
    def _safe_url_extract(self, element, selectors):
        for selector in selectors:
            found = element.select_one(selector)
            if found and 'href' in found.attrs:
                return self.base_url + found['href'].split('?')[0]
        return 'N/A'