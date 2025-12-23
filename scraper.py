import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,th;q=0.8,zh-CN;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def get_superrich_rates():
    """
    Fetches CNY rates from SuperRich Thailand.
    SuperRich has an API but may require specific headers.
    """
    # Try the API first
    api_url = "https://www.superrichthailand.com/api/v1/rates"
    
    try:
        headers = HEADERS.copy()
        headers['Referer'] = 'https://www.superrichthailand.com/'
        
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Look for CNY in the rates
            for currency in data.get('data', {}).get('rates', []):
                if currency.get('cUnit') == 'CNY':
                    rates = currency.get('rate', [])
                    if rates:
                        # Usually the first rate is for higher denominations (best rate)
                        return {
                            'provider': 'SuperRich Thailand',
                            'buying_tt': float(rates[0].get('cBuying', 0)),
                            'selling_tt': float(rates[0].get('cSelling', 0)),
                            'status': 'success',
                            'timestamp': datetime.now().isoformat()
                        }
        
        # Fallback: Return manual rate for demo purposes
        logging.warning(f"SuperRich API returned {response.status_code}, using fallback")
        return {
            'provider': 'SuperRich Thailand',
            'buying_tt': 4.52,  # Approximate current rate for demo
            'selling_tt': 4.55,
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'note': 'Using approximate rate - API may require authentication'
        }
        
    except Exception as e:
        logging.error(f"Error fetching SuperRich rates: {e}")
        return {
            'provider': 'SuperRich Thailand',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_kbank_rates():
    """
    Kasikorn Bank - Protected by WAF, will use fallback
    Real implementation would need Selenium/Playwright
    """
    try:
        # K-Bank blocks direct requests, would need browser automation
        # For now, return fallback with note
        return {
            'provider': 'K-Bank (Kasikorn)',
            'buying_tt': 4.48,
            'selling_tt': 4.58,
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'note': 'Site requires browser automation - using approximate rate'
        }
    except Exception as e:
        logging.error(f"Error fetching K-Bank rates: {e}")
        return {
            'provider': 'K-Bank (Kasikorn)',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_scb_rates():
    """
    SCB (Siam Commercial Bank) - Has API endpoint
    """
    try:
        # SCB has a service endpoint for rates
        url = "https://www.scb.co.th/services/scb/exchangeRateService.json"
        
        headers = HEADERS.copy()
        headers['Referer'] = 'https://www.scb.co.th/en/personal-banking/foreign-exchange-rates.html'
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Look for CNY in the rates
            for rate_entry in data.get('exchangeRateServiceResponse', {}).get('fxRateList', []):
                if rate_entry.get('currencyCode') == 'CNY':
                    return {
                        'provider': 'SCB',
                        'buying_tt': float(rate_entry.get('ttBuying', 0)),
                        'selling_tt': float(rate_entry.get('ttSelling', 0)),
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    }
        
        # Fallback
        return {
            'provider': 'SCB',
            'buying_tt': 4.45,
            'selling_tt': 4.60,
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'note': 'Using approximate rate'
        }
        
    except Exception as e:
        logging.error(f"Error fetching SCB rates: {e}")
        return {
            'provider': 'SCB',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_krungsri_rates():
    """
    Krungsri Bank (Bank of Ayudhya) - Protected by Incapsula
    """
    try:
        # Krungsri uses Incapsula protection, needs browser automation
        return {
            'provider': 'Krungsri Bank',
            'buying_tt': 4.47,
            'selling_tt': 4.59,
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'note': 'Site requires browser automation - using approximate rate'
        }
    except Exception as e:
        logging.error(f"Error fetching Krungsri rates: {e}")
        return {
            'provider': 'Krungsri Bank',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_bangkok_bank_rates():
    """
    Bangkok Bank - May have API or require scraping
    """
    try:
        # Bangkok Bank may have an API endpoint
        # For now using fallback
        return {
            'provider': 'Bangkok Bank',
            'buying_tt': 4.46,
            'selling_tt': 4.59,
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'note': 'Using approximate rate - API endpoint to be determined'
        }
    except Exception as e:
        logging.error(f"Error fetching Bangkok Bank rates: {e}")
        return {
            'provider': 'Bangkok Bank',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_boc_rates():
    """
    Bank of China (Thailand) - Chinese language site
    """
    try:
        # BOC Thailand may have rates, needs investigation
        return {
            'provider': 'Bank of China (TH)',
            'buying_tt': 4.49,
            'selling_tt': 4.58,
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'note': 'Using approximate rate'
        }
    except Exception as e:
        logging.error(f"Error fetching BOC rates: {e}")
        return {
            'provider': 'Bank of China (TH)',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_icbc_rates():
    """
    ICBC (Industrial and Commercial Bank of China) Thailand
    """
    try:
        # ICBC Thailand - Chinese site, may need specific parsing
        url = "https://www.icbcthai.com/ICBC/海外分行/工银泰国网站/cn/个人金融服务/其他/外汇汇率/外汇汇率.htm"
        
        headers = HEADERS.copy()
        headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Would need to parse the HTML table
            # For now, using fallback
            pass
        
        return {
            'provider': 'ICBC (Thailand)',
            'buying_tt': 4.48,
            'selling_tt': 4.57,
            'status': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'note': 'Using approximate rate'
        }
        
    except Exception as e:
        logging.error(f"Error fetching ICBC rates: {e}")
        return {
            'provider': 'ICBC (Thailand)',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def fetch_all_rates(include_all=False):
    """
    Aggregates rates from sources.
    
    Args:
        include_all: If True, fetch all sources. If False, only Thai banks for public display.
    
    Returns list of rate dictionaries.
    """
    logging.info("Fetching rates from providers...")
    
    results = []
    
    # Always fetch SuperRich as reference (for backend use)
    try:
        superrich_rate = get_superrich_rates()
        results.append(superrich_rate)
    except Exception as e:
        logging.error(f"Failed to fetch SuperRich (reference): {e}")
    
    # Thai banks for public display
    thai_banks = [
        get_kbank_rates,
        get_scb_rates,
        get_krungsri_rates,
        get_bangkok_bank_rates
    ]
    
    for provider_func in thai_banks:
        try:
            rate = provider_func()
            results.append(rate)
            time.sleep(0.5)  # Be polite to servers
        except Exception as e:
            logging.error(f"Failed to fetch from {provider_func.__name__}: {e}")
    
    # Only include Chinese banks if specifically requested
    if include_all:
        chinese_banks = [get_boc_rates, get_icbc_rates]
        for provider_func in chinese_banks:
            try:
                rate = provider_func()
                results.append(rate)
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Failed to fetch from {provider_func.__name__}: {e}")
    
    logging.info(f"Successfully fetched {len(results)} rate sources")
    return results

if __name__ == "__main__":
    rates = fetch_all_rates()
    print(json.dumps(rates, indent=2, ensure_ascii=False))
