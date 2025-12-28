import requests
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.chinamoney.com.cn/chinese/index.html'
}

def test_pboc():
    # This is a public data endpoint for CFETS
    url = "https://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # The JSON contains a list of rates
            for row in data.get('records', []):
                if row.get('vbtccy') == 'CNY/THB':
                    rate = float(row.get('vbtprice'))
                    print(f"PBOC success: {rate}")
                    return rate
    except Exception as e:
        print(f"PBOC error: {e}")

if __name__ == "__main__":
    test_pboc()
