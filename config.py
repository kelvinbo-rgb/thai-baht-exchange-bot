import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LINE Bot credentials (to be set in environment variables)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '').strip()
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '').strip()

if not LINE_CHANNEL_ACCESS_TOKEN:
    print("❌ ERROR: LINE_CHANNEL_ACCESS_TOKEN not found in environment settings!")
    
if not LINE_CHANNEL_SECRET:
    print("❌ ERROR: LINE_CHANNEL_SECRET not found in environment settings!")

# Admin user IDs (LINE user IDs)
# To get your LINE user ID, send a message to the bot and check the logs
ADMIN_USER_IDS = os.getenv('ADMIN_USER_IDS', '').split(',')

# Rate update schedule (minutes)
RATE_UPDATE_INTERVAL = int(os.getenv('RATE_UPDATE_INTERVAL', '30'))

# Alert check interval (minutes)
ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', '30'))

# Database path
DATABASE_PATH = os.getenv('DATABASE_PATH', 'exchange_bot.db')

# Server configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
