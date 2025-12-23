def find_best_rate(rates, rate_type='buying_tt'):
    """
    Finds the best TT rate from a list of rate providers.
    Higher buying rate is better for the user (provider pays more THB for CNY).
    
    Args:
        rates: List of rate dictionaries
        rate_type: 'buying_tt' or 'selling_tt'
    
    Returns:
        Dictionary of best rate provider
    """
    valid_rates = [r for r in rates if r.get('status') in ['success', 'fallback'] and r.get(rate_type)]
    
    if not valid_rates:
        return None
    
    # For buying (we sell CNY to them), higher is better
    # For selling (we buy CNY from them), lower is better
    if rate_type == 'buying_tt':
        best = max(valid_rates, key=lambda x: x[rate_type])
    else:
        best = min(valid_rates, key=lambda x: x[rate_type])
    
    return best

def calculate_exchange(amount_cny, rate):
    """Calculates the amount of THB received."""
    return amount_cny * rate

def format_rate_comparison(rates, highlight_provider='SuperRich Thailand'):
    """
    Formats rates for display with highlighting.
    
    Returns:
        String formatted for LINE message
    """
    if not rates:
        return "❌ 无法获取汇率数据 (Unable to fetch rate data)"
    
    # Sort by buying rate descending
    valid_rates = [r for r in rates if r.get('status') in ['success', 'fallback']]
    valid_rates.sort(key=lambda x: x.get('buying_tt', 0), reverse=True)
    
    output = "💱 **CNY → THB 电汇汇率**\n"
    output += "=" * 30 + "\n\n"
    
    for idx, rate in enumerate(valid_rates, 1):
        provider = rate['provider']
        buying = rate.get('buying_tt', 0)
        selling = rate.get('selling_tt', 0)
        
        # Highlight best rate and SuperRich
        prefix = ""
        if idx == 1:
            prefix = "🏆 "
        elif highlight_provider in provider:
            prefix = "⭐ "
        
        status_icon = "✅" if rate['status'] == 'success' else "📊"
        
        output += f"{prefix}{status_icon} **{provider}**\n"
        output += f"   买入: {buying:.4f} | 卖出: {selling:.4f}\n\n"
    
    return output

def get_exchange_summary(rates, amount_cny=1000, custom_rate=None, highlight_provider='优选汇率'):
    """
    Generates a comprehensive summary with calculation.
    
    Args:
        rates: List of rate dictionaries
        amount_cny: Amount in CNY to calculate
        custom_rate: User's custom rate dictionary
        highlight_provider: Provider to highlight (defaults to custom rate)
    
    Returns:
        Formatted string for LINE message
    """
    # Filter out SuperRich, BOC, ICBC from public display
    public_rates = [r for r in rates if r.get('provider') not in [
        'SuperRich Thailand', 'Bank of China (TH)', 'ICBC (Thailand)'
    ] and r.get('status') in ['success', 'fallback']]
    
    # Add custom rate if provided
    if custom_rate and custom_rate.get('status') == 'custom':
        public_rates.insert(0, custom_rate)  # Put custom rate first
    
    best_deal = find_best_rate(public_rates, 'buying_tt')
    
    if not best_deal:
        return "❌ 当前无法获取有效汇率数据\n(No valid rate data available)"
    
    summary = "💰 **人民币兑换泰铢 CNY → THB**\n"
    summary += "=" * 35 + "\n\n"
    
    # Show calculation
    summary += f"💵 计算金额: **{amount_cny:,.0f} CNY**\n\n"
    
    # Best rate
    best_thb = calculate_exchange(amount_cny, best_deal['buying_tt'])
    summary += f"🏆 **最佳汇率**: {best_deal['provider']}\n"
    summary += f"   汇率: {best_deal['buying_tt']:.4f}\n"
    summary += f"   可得: **{best_thb:,.2f} THB**\n\n"
    
    # Custom rate comparison if different from best
    if custom_rate and custom_rate != best_deal:
        custom_thb = calculate_exchange(amount_cny, custom_rate['buying_tt'])
        diff = best_thb - custom_thb
        summary += f"⭐ **{custom_rate['provider']}**: {custom_rate['buying_tt']:.2f}\n"
        summary += f"   可得: {custom_thb:,.2f} THB\n"
        if diff != 0:
            summary += f"   差额: {diff:+,.2f} THB\n"
        summary += "\n"
    
    # Rate status indicator
    if best_deal['buying_tt'] >= 4.55:
        summary += "🟢 **汇率状态**: 高位,适合兑换!\n"
    elif best_deal['buying_tt'] >= 4.50:
        summary += "🟡 **汇率状态**: 正常水平\n"
    else:
        summary += "🔴 **汇率状态**: 偏低,建议等待\n"
    
    summary += "\n" + "=" * 35 + "\n"
    summary += "💡 输入 '汇率' 查看所有银行对比\n"
    summary += "💡 输入 '计算 金额' 自定义计算"
    
    return summary

def format_all_rates_table(rates, custom_rate=None):
    """
    Format all rates in a detailed table for LINE display.
    Only shows Thai banks + custom rate (no SuperRich, BOC, ICBC).
    """
    # Filter to only public rates (Thai banks)
    public_rates = [r for r in rates if r.get('provider') not in [
        'SuperRich Thailand', 'Bank of China (TH)', 'ICBC (Thailand)'
    ] and r.get('status') in ['success', 'fallback']]
    
    # Add custom rate at the top if provided
    if custom_rate and custom_rate.get('status') == 'custom':
        public_rates.insert(0, custom_rate)
    
    comparison = format_rate_comparison(public_rates, highlight_provider=custom_rate.get('provider') if custom_rate else '优选汇率')
    
    best = find_best_rate(public_rates, 'buying_tt')
    
    if not best:
        return "❌ 暂无汇率数据"
    
    footer = f"\n💡 **建议**: 在 {best['provider']} 兑换最划算\n"
    footer += f"当前最佳买入价: **{best['buying_tt']:.2f}**\n\n"
    footer += "📌 提示:\n"
    footer += "• 买入= 您卖CNY给我们的价格(重点)\n"
    footer += "• 卖出 = 您从我们买CNY的价格\n"
    footer += "• 输入 '计算 金额' 试算兑换结果"
    
    return comparison + footer

if __name__ == "__main__":
    # Test data
    sample_rates = [
        {'provider': 'SuperRich Thailand', 'buying_tt': 4.52, 'selling_tt': 4.55, 'status': 'success'},
        {'provider': 'K-Bank (Kasikorn)', 'buying_tt': 4.48, 'selling_tt': 4.58, 'status': 'fallback'},
        {'provider': 'SCB', 'buying_tt': 4.45, 'selling_tt': 4.60, 'status': 'success'},
        {'provider': 'Krungsri Bank', 'buying_tt': 4.47, 'selling_tt': 4.59, 'status': 'fallback'},
        {'provider': 'Bangkok Bank', 'buying_tt': 4.46, 'selling_tt': 4.59, 'status': 'fallback'},
        {'provider': 'Bank of China (TH)', 'buying_tt': 4.49, 'selling_tt': 4.58, 'status': 'fallback'},
        {'provider': 'ICBC (Thailand)', 'buying_tt': 4.48, 'selling_tt': 4.57, 'status': 'fallback'}
    ]
    
    print(get_exchange_summary(sample_rates, 5000))
    print("\n" + "="*50 + "\n")
    print(format_all_rates_table(sample_rates))
