from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import re

# Import our modules
from scraper import fetch_all_rates
from calculator import get_exchange_summary, format_all_rates_table
from database import init_database, save_rate_history, is_admin
from queue_manager import join_queue, get_queue_status, get_next_customer, mark_completed, get_full_queue, leave_queue
from alerts import create_alert, cancel_alert, check_alerts_and_notify
from custom_rate import get_custom_rate, set_custom_rate, auto_set_from_bot
import config

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize LINE Bot API
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

# Initialize database
init_database()

# Global variable to store latest rates
latest_rates = []

def update_rates():
    """Background task to update exchange rates."""
    global latest_rates
    try:
        logger.info("Updating exchange rates...")
        latest_rates = fetch_all_rates()
        save_rate_history(latest_rates)
        logger.info(f"Successfully updated {len(latest_rates)} rates")
    except Exception as e:
        logger.error(f"Error updating rates: {e}")

def check_and_send_alerts():
    """Background task to check alerts and send notifications."""
    try:
        logger.info("Checking rate alerts...")
        notifications = check_alerts_and_notify()
        
        for notif in notifications:
            try:
                line_bot_api.push_message(
                    notif['user_id'],
                    TextSendMessage(text=notif['message'])
                )
                logger.info(f"Sent alert to {notif['user_name']}")
            except Exception as e:
                logger.error(f"Failed to send alert to {notif['user_id']}: {e}")
                
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")

# Initialize scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_rates, trigger="interval", minutes=config.RATE_UPDATE_INTERVAL)
scheduler.add_job(func=check_and_send_alerts, trigger="interval", minutes=config.ALERT_CHECK_INTERVAL)
scheduler.start()

# Initial rate fetch
update_rates()

@app.route("/callback", methods=['POST'])
def callback():
    """LINE Bot webhook callback."""
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    logger.info("="*60)
    logger.info("✅ Received webhook request")
    logger.info(f"Signature: {signature[:20]}...")
    logger.info(f"Body length: {len(body)}")
    logger.info("="*60)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your LINE_CHANNEL_SECRET.")
        abort(400)
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """Handle incoming text messages."""
    user_id = event.source.user_id
    text = event.message.text.strip()
    
    try:
        # Get user profile
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name
    except:
        user_name = "User"
    
    # Detect source type (User, Group, Room)
    source_type = event.source.type
    group_id = event.source.group_id if source_type == 'group' else None
    
    # 🔥 重要: 打印 USER ID & 来源 供管理员配置使用
    logger.info("="*60)
    logger.info(f"📨 收到消息 [{'群聊' if source_type == 'group' else '私聊'}]")
    if group_id:
        logger.info(f"👥 Group ID: {group_id}")
    logger.info(f"👤 用户名: {user_name}")
    logger.info(f"🆔 USER ID: {user_id}")
    logger.info(f"💬 消息内容: {text}")
    logger.info("="*60)
    
    # 如果.env中ADMIN_USER_IDS为空,提示用户
    if not config.ADMIN_USER_IDS or config.ADMIN_USER_IDS == ['']:
        logger.warning("⚠️  ADMIN_USER_IDS 未设置!")
        logger.warning(f"⚠️  请将以下 USER ID 添加到 .env 文件:")
        logger.warning(f"⚠️  ADMIN_USER_IDS={user_id}")
    
    # Command routing
    response = route_command(user_id, user_name, text)
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

def route_command(user_id, user_name, text):
    """Route user commands to appropriate handlers."""
    text_lower = text.lower()
    
    # Rate display commands
    if text_lower in ['汇率', 'rate', 'rates', '查汇率']:
        return handle_rate_display()
    
    # Calculation commands
    calc_match = re.match(r'(计算|calc|calculate)\s*(\d+\.?\d*)', text_lower)
    if calc_match:
        amount = float(calc_match.group(2))
        return handle_calculation(amount)
    
    # Queue commands
    if text_lower in ['排队', 'queue', 'join']:
        return handle_join_queue(user_id, user_name)
    
    if text_lower in ['位置', 'status', 'position', '我的位置']:
        return handle_queue_status(user_id)
    
    if text_lower in ['离开', 'leave', '退出排队']:
        return handle_leave_queue(user_id)
    
    # Alert commands
    alert_match = re.match(r'(预警|alert)\s+(\d+\.?\d*)', text_lower)
    if alert_match:
        target_rate = float(alert_match.group(2))
        return handle_create_alert(user_id, user_name, target_rate)
    
    if text_lower in ['取消预警', 'cancel alert', 'cancel']:
        return handle_cancel_alert(user_id)
    
    # Admin commands
    if is_admin(user_id) or user_id in config.ADMIN_USER_IDS:
        # Set custom rate manually
        set_rate_match = re.match(r'(设置汇率|setrate)\s+(\d+\.?\d*)', text_lower)
        if set_rate_match:
            rate_value = float(set_rate_match.group(2))
            return handle_set_custom_rate(rate_value)
        
        # Auto set from BOT
        if text_lower in ['自动设置', 'auto', 'autoset']:
            return handle_auto_set_rate()
        
        # Queue management
        if text_lower in ['下一个', 'next', '下一位']:
            return handle_next_customer()
        
        if text_lower in ['完成', 'done', 'complete']:
            return handle_complete_customer()
        
        if text_lower in ['队列', 'queue list', '查看队列']:
            return handle_view_queue()
    
    # Help / Default
    return handle_help()

def handle_rate_display():
    """Display all exchange rates."""
    if not latest_rates:
        return "⏳ 正在获取最新汇率,请稍后..."
    
    custom_rate = get_custom_rate()
    return format_all_rates_table(latest_rates, custom_rate)

def handle_calculation(amount):
    """Calculate exchange for specified amount."""
    if not latest_rates:
        return "⏳ 正在获取最新汇率,请稍后..."
    
    if amount <= 0:
        return "❌ 请输入有效的金额 (大于0)"
    
    custom_rate = get_custom_rate()
    return get_exchange_summary(latest_rates, amount, custom_rate)

def handle_join_queue(user_id, user_name):
    """Handle user joining the queue."""
    result = join_queue(user_id, user_name)
    
    if result['status'] == 'already_in_queue':
        return f"您已在队列中!\n\n您前面还有 {result['position'] - 1} 人\n\n输入 '位置' 查看实时状态"
    else:
        ahead = result['position'] - 1
        return f"✅ 已加入队列!\n\n您的位置: 第 {result['position']} 位\n前面还有: {ahead} 人\n\n请耐心等待,我们会按顺序处理。\n输入 '位置' 随时查看进度"

def handle_queue_status(user_id):
    """Handle queue status inquiry."""
    status = get_queue_status(user_id)
    
    if not status['in_queue']:
        return "您目前不在队列中\n\n输入 '排队' 加入队列"
    
    return f"📋 您的排队状态\n\n位置: 第 {status['position']} 位\n前面还有: {status['ahead']} 人\n\n请耐心等待,我们正在按顺序处理"

def handle_leave_queue(user_id):
    """Handle user leaving the queue."""
    success = leave_queue(user_id)
    
    if success:
        return "✅ 已离开队列"
    else:
        return "您不在队列中"

def handle_create_alert(user_id, user_name, target_rate):
    """Handle creating a rate alert."""
    if target_rate < 3.0 or target_rate > 6.0:
        return "❌ 汇率设置不合理 (建议范围: 3.0 - 6.0)"
    
    result = create_alert(user_id, user_name, target_rate, 'above')
    return result['message']

def handle_cancel_alert(user_id):
    """Handle canceling alerts."""
    result = cancel_alert(user_id)
    return result['message']

def handle_next_customer():
    """Admin: Get next customer from queue."""
    customer = get_next_customer()
    
    if not customer:
        return "✅ 队列为空,没有等待的客户"
    
    # Notify the customer
    try:
        message = "🔔 轮到您了!\n\n请准备好您的兑换需求,我们即将为您处理。"
        line_bot_api.push_message(
            customer['user_id'],
            TextSendMessage(text=message)
        )
    except Exception as e:
        logger.error(f"Failed to notify customer: {e}")
    
    return f"📋 下一位客户:\n\n姓名: {customer['user_name']}\n加入时间: {customer['created_at']}\n\n已通知客户。处理完成后输入 '完成'"

def handle_complete_customer():
    """Admin: Mark current customer as completed."""
    # Get the processing customer
    full_queue = get_full_queue()
    processing = [c for c in full_queue if c['status'] == 'processing']
    
    if not processing:
        return "❌ 当前没有正在处理的客户"
    
    customer = processing[0]
    mark_completed(customer['queue_id'])
    
    # Notify customer
    try:
        message = "✅ 您的业务已处理完成,感谢您的耐心等待!"
        line_bot_api.push_message(
            customer['user_id'],
            TextSendMessage(text=message)
        )
    except Exception as e:
        logger.error(f"Failed to notify customer: {e}")
    
    return f"✅ 已完成: {customer['user_name']}\n\n输入 '下一个' 处理下一位客户"

def handle_view_queue():
    """Admin: View full queue."""
    queue = get_full_queue()
    
    if not queue:
        return "✅ 队列为空"
    
    response = f"📋 当前队列 ({len(queue)} 人)\n\n"
    
    for idx, customer in enumerate(queue, 1):
        status_icon = "🔄" if customer['status'] == 'processing' else "⏳"
        response += f"{idx}. {status_icon} {customer['user_name']}\n"
        response += f"   {customer['created_at']}\n\n"
    
    return response

def handle_set_custom_rate(rate_value):
    """Admin: Set custom exchange rate manually."""
    if rate_value < 3.0 or rate_value > 6.0:
        return "❌ 汇率设置超出合理范围 (3.0 - 6.0)"
    
    result = set_custom_rate(rate_value)
    
    return f"✅ 已设置优选汇率\n\n买入价: {result['buying_tt']:.2f}\n卖出价: {result['selling_tt']:.2f}\n\n提示: 汇率已自动调整为0.05的倍数"

def handle_auto_set_rate():
    """Admin: Auto-set rate from BOT."""
    from custom_rate import auto_set_from_bot
    
    # Find BOT rate from latest rates
    bot_ref = next((r for r in latest_rates if '泰国央行' in r.get('provider', '')), None)
    
    if not bot_ref or bot_ref.get('status') not in ['success', 'fallback']:
        return "❌ 无法获取泰国央行参考汇率"
    
    # Auto set from BOT
    result = auto_set_from_bot(bot_ref)
    
    if not result:
        return "❌ 自动设置汇率失败"
        
    return f"✅ 已根据泰国央行自动设置汇率\n\n参考汇率: {bot_ref['buying_tt']:.4f}\n设置买入: {result['buying_tt']:.2f}\n设置卖出: {result['selling_tt']:.2f}\n\n提示: 优选买入已按0/5取整，卖出已增加0.20点差"

def handle_help():
    """Display help message."""
    help_text = """
🤖 **泰铢汇率查询**

📊 **查询汇率**
• 汇率 - 查看所有对比 (含央行、Google财经)
• 计算 [金额] - 试算兑换结果 (如: 计算5000)

📋 **排队功能**
• 排队 - 加入客户队列
• 位置 - 查看排队状态
• 离开 - 退出队列

🔔 **汇率预警**
• 预警 [汇率] - 设置提醒 (如: 预警 4.55)
• 取消预警 - 关闭提醒

💡 **提示**: 
• 数据源: 泰国央行、Google财经、国际中间价
• 优选汇率已按0/5取整 (如 4.50, 4.55)
• 卖出价已包含标准点差 (+0.20)
"""
    return help_text.strip()

@app.route("/")
def home():
    """Home page."""
    return """
    <h1>泰铢汇率查询 LINE Bot</h1>
    <p>Thai Baht Exchange Rate LINE Bot</p>
    <p>Status: <strong>Running</strong></p>
    <p>Add the bot on LINE to get started!</p>
    """

@app.route("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "rates_count": len(latest_rates)}

if __name__ == "__main__":
    try:
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()