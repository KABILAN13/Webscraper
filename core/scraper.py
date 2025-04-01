from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random

class BaseScraper(ABC):
    def __init__(self, use_selenium=False):
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.google.com/'
        }
        
    @abstractmethod
    def parse_product_page(self, url):
        pass
    
    @abstractmethod
    def search_products(self, query):
        pass
    
    def get_page(self, url):
        if self.use_selenium:
            return self._get_page_selenium(url)
        else:
            return self._get_page_requests(url)
    
    def _get_page_requests(self, url):
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def _get_page_selenium(self, url):
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    
    # Rotate user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                              options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
            driver.get(url)
        # Wait for either search results or product page
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component-type="s-search-result"], #productTitle'))
                )
            except:
                pass  # Continue even if not all elements loaded
        
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return soup
        finally:
            driver.quit()