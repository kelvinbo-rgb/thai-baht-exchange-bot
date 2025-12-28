import requests
import json
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def test_yahoo():
    # Yahoo Finance Chart API (often works without auth)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/CNYTHB=X?interval=1m&range=1d"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rate = data['chart']['result'][0]['meta']['regularMarketPrice']
            print(f"Yahoo success: {rate}")
            return rate
    except Exception as e:
        print(f"Yahoo error: {e}")

def test_sina_v2():
    # Try the web-friendly version
    url = "https://hq.sinajs.cn/list=CNYTHB"
    headers = HEADERS.copy()
    headers['Referer'] = 'https://finance.sina.com.cn/'
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Sina response is often GBK
        content = response.content.decode('gbk')
        print(f"Sina raw: {content}")
        if '"' in content:
            match = content.split('"')[1]
            if match:
                parts = match.split(',')
                # For CNYTHB, usually parts[1] or parts[3] is the price
                # We need to verify which part. Usually the one around 4.4...
                for p in parts:
                    try:
                        val = float(p)
                        if 4.0 < val < 5.0:
                            print(f"Sina guess: {val}")
                            return val
                    except: pass
    except Exception as e:
        print(f"Sina error: {e}")

if __name__ == "__main__":
    test_yahoo()
    test_sina_v2()
