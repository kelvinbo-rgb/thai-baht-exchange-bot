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
    valid_rates = [r for r in rates if r.get('status') in ['success', 'fallback', 'custom'] and r.get(rate_type)]
    
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

def format_rate_comparison(rates, highlight_provider='优选汇率'):
    """
    Formats rates for display with highlighting.
    
    Returns:
        String formatted for LINE message
    """
    if not rates:
        return "❌ 无法获取汇率数据 (Unable to fetch rate data)"
    
    # Sort by buying rate descending
    valid_rates = [r for r in rates if r.get('status') in ['success', 'fallback', 'custom']]
    # Custom rate should always be at the top if it exists
    valid_rates.sort(key=lambda x: (x.get('status') == 'custom', x.get('buying_tt', 0)), reverse=True)
    
    output = "💱 **CNY → THB 电汇汇率**\n"
    output += "=" * 30 + "\n\n"
    
    for idx, rate in enumerate(valid_rates, 1):
        provider = rate['provider']
        buying = rate.get('buying_tt', 0)
        selling = rate.get('selling_tt', 0)
        
        # Highlight custom rate and best market rate
        prefix = ""
        if rate.get('status') == 'custom':
            prefix = "⭐ "
        elif idx == 1 or (idx == 2 and valid_rates[0].get('status') == 'custom'):
            prefix = "🏆 "
        
        status_icon = "✅" if rate['status'] in ['success', 'custom'] else "📊"
        
        output += f"{prefix}{status_icon} **{provider}**\n"
        output += f"   买入: {buying:.4f} | 卖出: {selling:.4f}\n\n"
    
    return output

def get_exchange_summary(rates, amount_cny=1000, custom_rate=None, highlight_provider='优选汇率'):
    """
    Generates a comprehensive summary with calculation.
    """
    # Filter public display: Focus on reliable references
    public_sources = ['泰国央行参考价', 'Google财经', '国际中间价', 'Yahoo财经', '中国银行(泰国)']
    public_rates = [r for r in rates if r.get('provider') in public_sources and r.get('status') in ['success', 'fallback']]
    
    # Add custom rate if provided
    active_rates = list(public_rates)
    if custom_rate and custom_rate.get('status') == 'custom':
        active_rates.insert(0, custom_rate)
    
    best_deal = find_best_rate(active_rates, 'buying_tt')
    
    if not active_rates:
        return "❌ 当前无法获取有效汇率数据\n(No valid rate data available)"
    
    summary = "💰 **人民币兑换泰铢 CNY → THB**\n"
    summary += "=" * 35 + "\n\n"
    
    # Show calculation
    summary += f"💵 计算金额: **{amount_cny:,.0f} CNY**\n\n"
    
    # Preferred rate (Custom) if exists
    target_rate = custom_rate if custom_rate else best_deal
    if target_rate:
        target_thb = calculate_exchange(amount_cny, target_rate['buying_tt'])
        summary += f"⭐ **{target_rate['provider']}**: {target_rate['buying_tt']:.4f}\n"
        summary += f"   可得: **{target_thb:,.2f} THB**\n\n"
    
    # Market Best comparison if different
    market_best = find_best_rate(public_rates, 'buying_tt')
    if market_best and market_best != target_rate:
        market_thb = calculate_exchange(amount_cny, market_best['buying_tt'])
        summary += f"🏆 **市场最高**: {market_best['provider']}\n"
        summary += f"   汇率: {market_best['buying_tt']:.4f}\n"
        summary += f"   可得: {market_thb:,.2f} THB\n"
        
        diff = target_thb - market_thb
        if diff < 0:
            summary += f"   (差额: {diff:,.2f} THB)\n"
        summary += "\n"
    
    # Rate status indicator
    ref_rate = target_rate['buying_tt']
    if ref_rate >= 4.55:
        summary += "🟢 **汇率状态**: 高位,适合兑换!\n"
    elif ref_rate >= 4.45:
        summary += "🟡 **汇率状态**: 正常水平\n"
    else:
        summary += "🔴 **汇率状态**: 偏低,建议等待\n"
    
    summary += "\n" + "=" * 35 + "\n"
    summary += "💡 输入 '汇率' 查看详细对比\n"
    summary += "💡 输入 '计算金额' (如: 计算5000) 试算\n"
    summary += "💡 输入 '排队' 或 '人工' 获取更多服务"
    
    return summary

def format_all_rates_table(rates, custom_rate=None):
    """
    Format all rates in a detailed table for LINE display.
    """
    # Filter to only approved public rates
    public_sources = ['泰国央行参考价', 'Google财经', '国际中间价', 'Yahoo财经', '中国银行(泰国)']
    public_rates = [r for r in rates if r.get('provider') in public_sources and r.get('status') in ['success', 'fallback']]
    
    # Prepare full list for comparison
    comparison_list = list(public_rates)
    if custom_rate and custom_rate.get('status') == 'custom':
        comparison_list.insert(0, custom_rate)
    
    highlight_name = custom_rate.get('provider') if custom_rate else '优选汇率'
    comparison = format_rate_comparison(comparison_list, highlight_provider=highlight_name)
    
    best_market = find_best_rate(public_rates, 'buying_tt')
    rec_provider = custom_rate.get('provider') if custom_rate else (best_market['provider'] if best_market else "优选汇率")
    
    footer = f"\n💡 **建议**\n推荐使用 [**{rec_provider}**] 兑换\n"
    if custom_rate:
        footer += f"当前优选买入价: **{custom_rate['buying_tt']:.2f}**\n\n"
    
    footer += "📌 **温馨提示**\n"
    footer += "• 买入 = 我们付给您的价格(越优越好)\n"
    footer += "• 卖出 = 您向我们购买的价格\n"
    footer += "• 输入 '计算金额' (如: 计算5000) 快速试算\n"
    footer += "• 输入 '排队' 加入办理队列\n"
    footer += "• 输入 '位置' 或 '离开' 查看/退出队列\n"
    footer += "• 输入 '人工' 直接联系管理员咨询"
    
    return comparison + footer
