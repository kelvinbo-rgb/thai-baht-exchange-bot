import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Storage file for custom rates
RATE_FILE = 'custom_rate.json'

def round_to_05(value):
    """
    Rounds a value to the nearest 0.05.
    Examples: 4.512 -> 4.50, 4.537 -> 4.55, 4.563 -> 4.55
    """
    return round(value * 20) / 20

def set_custom_rate(buying_tt, selling_tt=None, provider_name="优选汇率"):
    """
    Set custom exchange rate.
    Automatically rounds to nearest 0.05.
    
    Args:
        buying_tt: Buying TT rate (what you pay customers for their CNY)
        selling_tt: Selling TT rate (optional, defaults to buying + 0.20)
        provider_name: Display name for your rates
    """
    # Round to nearest 0.05
    buying_rounded = round_to_05(buying_tt)
    
    if selling_tt is None:
        # Default spread: 20 pips (0.20)
        selling_rounded = buying_rounded + 0.20
    else:
        selling_rounded = round_to_05(selling_tt)
    
    rate_data = {
        'provider': provider_name,
        'buying_tt': buying_rounded,
        'selling_tt': selling_rounded,
        'status': 'custom',
        'timestamp': datetime.now().isoformat(),
        'last_updated_by': 'admin'
    }
    
    # Save to file
    try:
        with open(RATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(rate_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Custom rate set: Buy={buying_rounded}, Sell={selling_rounded}")
    except Exception as e:
        logging.error(f"Failed to save custom rate: {e}")
    
    return rate_data

def get_custom_rate():
    """
    Get the current custom exchange rate.
    Returns None if not set.
    """
    try:
        with open(RATE_FILE, 'r', encoding='utf-8') as f:
            rate_data = json.load(f)
        return rate_data
    except FileNotFoundError:
        logging.warning("No custom rate set yet")
        return None
    except Exception as e:
        logging.error(f"Failed to load custom rate: {e}")
        return None

def auto_set_from_bot(bot_rate, provider_name="优选汇率"):
    """
    Automatically set custom rate based on Bank of Thailand (BOT) rate.
    Logic: BOT rate rounded to 0/5. Sell = Buy + 0.20.
    """
    if bot_rate.get('status') not in ['success', 'fallback']:
        logging.error("Invalid BOT rate provided")
        return None
    
    base_rate = bot_rate.get('buying_tt', 0.0)
    if base_rate == 0.0:
        return None
        
    # logic: round to 0.05
    target_buy = round_to_05(base_rate)
    
    return set_custom_rate(target_buy, provider_name=provider_name)

if __name__ == "__main__":
    # Example usage
    print("Setting custom rate to 4.55...")
    rate = set_custom_rate(4.55)
    print(json.dumps(rate, indent=2, ensure_ascii=False))
    
    print("\nGetting custom rate...")
    current = get_custom_rate()
    print(json.dumps(current, indent=2, ensure_ascii=False))
    
    print("\nTesting rounding...")
    test_values = [4.512, 4.537, 4.563, 4.499, 4.474]
    for val in test_values:
        rounded = round_to_05(val)
        print(f"{val} -> {rounded}")
