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
        selling_tt: Selling TT rate (optional, defaults to buying + 0.05)
        provider_name: Display name for your rates
    
    Returns:
        Dictionary with rounded rates
    """
    # Round to nearest 0.05
    buying_rounded = round_to_05(buying_tt)
    
    if selling_tt is None:
        selling_rounded = buying_rounded + 0.05
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
        logging.info(f"Custom rate set: {buying_rounded} / {selling_rounded}")
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

def auto_set_from_superrich(superrich_rate, margin=0.0, provider_name="优选汇率"):
    """
    Automatically set custom rate based on SuperRich rate.
    
    Args:
        superrich_rate: SuperRich rate dictionary
        margin: Adjustment margin (e.g., -0.02 means 0.02 lower than SuperRich)
        provider_name: Display name
    
    Returns:
        Dictionary with custom rate
    """
    if superrich_rate.get('status') not in ['success', 'fallback']:
        logging.error("Invalid SuperRich rate provided")
        return None
    
    base_rate = superrich_rate.get('buying_tt', 4.50)
    adjusted_rate = base_rate + margin
    
    return set_custom_rate(adjusted_rate, provider_name=provider_name)

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
