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
    """Scrapes CNY/THB rate from Google Finance."""
    url = "https://www.google.com/finance/quote/CNY-THB?hl=en"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            price_element = soup.select_one('[data-last-price]')
            if price_element:
                rate_str = price_element.get('data-last-price')
                if rate_str:
                    rate = float(rate_str)
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

def get_yahoo_rates():
    """Fetches CNY/THB rate from Yahoo Finance Chart API."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/CNYTHB=X?interval=1m&range=1d"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            rate = data['chart']['result'][0]['meta']['regularMarketPrice']
            return {
                'provider': 'Yahoo财经',
                'buying_tt': float(rate),
                'selling_tt': float(rate),
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logging.error(f"Error fetching Yahoo Finance rate: {e}")
    return {'provider': 'Yahoo财经', 'status': 'error', 'timestamp': datetime.now().isoformat()}

def get_boc_th_rates():
    """Scrapes CNY/THB rate from Bank of China Thailand (Official Source)."""
    url = "https://www.bankofchina.com/sourcedb/thb/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='data2')
            if table:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if cells and 'CNY' in cells[0].text:
                        return {
                            'provider': '中国银行(泰国)',
                            'buying_tt': float(cells[1].text.strip() or 0),
                            'selling_tt': float(cells[2].text.strip() or 0),
                            'status': 'success',
                            'timestamp': datetime.now().isoformat()
                        }
    except Exception as e:
        logging.error(f"Error scraping BOC Thailand: {e}")
    return {'provider': '中国银行(泰国)', 'status': 'error', 'timestamp': datetime.now().isoformat()}

def get_open_api_rate():
    """Stable Open API rate (International Mid-rate)."""
    url = "https://open.er-api.com/v6/latest/CNY"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rate = float(data['rates']['THB'])
            return {
                'provider': '国际中间价',
                'buying_tt': rate,
                'selling_tt': rate,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logging.error(f"Error fetching Open API rate: {e}")
    return {'provider': '国际中间价', 'status': 'error', 'timestamp': datetime.now().isoformat()}

def get_bot_rates():
    """Bank of Thailand (BOT) reference rates."""
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
    """Aggregates all reliable rates."""
    logging.info("Fetching reliable rates from providers...")
    results = []
    
    # List of reliable scrapers
    scrapers = [
        get_google_rates,
        get_yahoo_rates,
        get_boc_th_rates,
        get_open_api_rate,
        get_bot_rates
    ]
    
    for scraper_func in scrapers:
        try:
            results.append(scraper_func())
            time.sleep(0.5) # Be gentle
        except Exception as e:
            logging.error(f"Failed in {scraper_func.__name__}: {e}")
    
    logging.info(f"Successfully fetched {len(results)} reliable rate sources")
    return results

if __name__ == "__main__":
    rates = fetch_all_rates()
    for r in rates:
        print(f"{r['provider']}: {r.get('buying_tt')} / {r.get('selling_tt')} [{r['status']}]")
