import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,th;q=0.8,zh-CN;q=0.7',
}

def test_boc_th():
    url = "https://www.bankofchina.com/sourcedb/thb/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='data2')
            if not table:
                print("BOC: Table not found")
                return
            
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if cells and 'CNY' in cells[0].text:
                    # Column indices based on subagent report:
                    # 0: Currency, 1: TT Buy, 2: TT Sell, 3: Cash Buy, 4: Cash Sell
                    data = {
                        'provider': '中国银行(泰国)',
                        'buying_tt': float(cells[1].text.strip() or 0),
                        'selling_tt': float(cells[2].text.strip() or 0),
                        'status': 'success'
                    }
                    print(f"BOC success: {data}")
                    return data
    except Exception as e:
        print(f"BOC error: {e}")

def test_sina():
    # Sina Finance via JS API
    url = "https://hq.sinajs.cn/list=fx_scnythb"
    headers = HEADERS.copy()
    headers['Referer'] = 'https://finance.sina.com.cn/'
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Format: var hq_str_fx_scnythb="time,open,low,high,last,..."
            content = response.text
            match = content.split('"')[1]
            if match:
                parts = match.split(',')
                # For Sina FX, parts[4] is usually the last price
                rate = float(parts[4])
                print(f"Sina success: {rate}")
                return rate
    except Exception as e:
        print(f"Sina error: {e}")

def test_pboc():
    # PBOC (CFETS) Middle Rate Fixing
    # Usually available at this endpoint
    url = "https://www.chinamoney.com.cn/ags/ms/fx/ccpr"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for record in data.get('records', []):
                if record.get('cpByccy') == 'CNY/THB':
                    rate = float(record.get('price'))
                    print(f"PBOC success: {rate}")
                    return rate
    except Exception as e:
        print(f"PBOC error: {e}")

if __name__ == "__main__":
    test_boc_th()
    test_sina()
    test_pboc()
