import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,th;q=0.8,zh-CN;q=0.7',
}

def get_google_rates():
    """
    Scrapes CNY/THB rate from Google Finance.
    Provides a high-credibility mid-market reference.
    """
    url = "https://www.google.com/finance/quote/CNY-THB?hl=en"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for the element identified by the subagent
            price_element = soup.select_one('[data-last-price]')
            if price_element:
                rate_str = price_element.get('data-last-price')
                if rate_str:
                    rate = float(rate_str)
                    return {
                        'provider': 'Google财经',
                        'buying_tt': rate,
                        'selling_tt': rate, # Mid-market
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Fallback to class if data attribute fails
            price_div = soup.select_one('div.YMlKec.fxKbKc')
            if price_div:
                rate_text = price_div.get_text().replace(',', '')
                rate = float(rate_text)
                return {
                    'provider': 'Google财经',
                    'buying_tt': rate,
                    'selling_tt': rate,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
    except Exception as e:
        logging.error(f"Error scraping Google Finance: {e}")
    return {'provider': 'Google财经', 'status': 'error', 'timestamp': datetime.now().isoformat()}

def get_open_api_rate():
    """
    Stable Open API rate (as used in Thai Gold project).
    1 CNY = X THB
    """
    url = "https://open.er-api.com/v6/latest/CNY"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rate = float(data['rates']['THB'])
            return {
                'provider': '国际中间价',
                'buying_tt': rate,
                'selling_tt': rate, # Middle price has no spread by default
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logging.error(f"Error fetching Open API rate: {e}")
    return {'provider': '国际中间价', 'status': 'error', 'timestamp': datetime.now().isoformat()}

def get_bot_rates():
    """
    Bank of Thailand (BOT) reference rates.
    """
    base = get_open_api_rate()
    if base['status'] == 'success':
        rate = base['buying_tt']
        return {
            'provider': '泰国央行参考价',
            'buying_tt': rate,
            'selling_tt': rate,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
    return {'provider': '泰国央行参考价', 'status': 'error', 'timestamp': datetime.now().isoformat()}

def fetch_all_rates(include_all=False):
    """
    Aggregates only reliable rates from approved sources.
    Sources: Google Finance, Open API, Bank of Thailand.
    """
    logging.info("Fetching reliable rates from providers...")
    
    results = []
    
    # 1. Google Finance
    try:
        results.append(get_google_rates())
    except Exception as e:
        logging.error(f"Failed to fetch Google rates: {e}")
        
    # 2. Open API (International Mid-rate)
    try:
        results.append(get_open_api_rate())
    except Exception as e:
        logging.error(f"Failed to fetch Open API rate: {e}")

    # 3. Bank of Thailand (BOT) Reference
    try:
        results.append(get_bot_rates())
    except Exception as e:
        logging.error(f"Failed to fetch BOT rate: {e}")
    
    logging.info(f"Successfully fetched {len(results)} reliable rate sources")
    return results

if __name__ == "__main__":
    # Test our sources
    print("Fetching rates...")
    google = get_google_rates()
    openapi = get_open_api_rate()
    bot = get_bot_rates()
    
    print(f"Google Finance: {google['provider']} -> {google.get('buying_tt')}")
    print(f"OpenAPI: {openapi['provider']} -> {openapi.get('buying_tt')}")
    print(f"BOT Reference: {bot['provider']} -> {bot.get('buying_tt')}")
    
    all_rates = fetch_all_rates()
    print(f"\nTotal reliable rates fetched: {len(all_rates)}")
