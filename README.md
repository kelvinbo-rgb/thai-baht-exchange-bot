# Thai Baht Exchange Rate LINE Bot

泰铢兑换汇率机器人 - LINE Bot for tracking and comparing CNY to THB exchange rates

## Features

### 🏦 Multi-Bank Rate Comparison
Track exchange rates from 7 major providers:
- SuperRich Thailand (primary focus)
- K-Bank (Kasikorn Bank)
- SCB (Siam Commercial Bank)
- Krungsri Bank
- Bangkok Bank
- Bank of China (Thailand)
- ICBC (Thailand)

### 💱 Smart Features
- **Real-time TT Rate Display** - All banks with SuperRich highlighted
- **Exchange Calculator** - Input any CNY amount to calculate THB
- **Rate Alerts** - Get notified when rates reach your target
- **Customer Queue** - Join queue and track your position
- **Admin Queue Management** - Process customers in FIFO order

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- LINE Developer Account
- A server with public URL (for webhook)

### 2. Create LINE Bot
1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create a new Messaging API channel
3. Get your **Channel Access Token** and **Channel Secret**
4. Set webhook URL to `https://your-domain.com/callback`

### 3. Installation

```bash
# Clone or navigate to the project directory
cd thai-baht-exchange-bot

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your LINE credentials
# Use a text editor to fill in:
# - LINE_CHANNEL_ACCESS_TOKEN
# - LINE_CHANNEL_SECRET
# - ADMIN_USER_IDS (you can get this after first message)
```

### 4. Initialize Database

```bash
python database.py
```

### 5. Test Scrapers (Optional)

```bash
python scraper.py
```

### 6. Run the Bot

```bash
python app.py
```

The bot will start on `http://0.0.0.0:5000`

### 7. Deploy to Production

For production, use a service like:
- **Railway**: One-click deploy with automatic HTTPS
- **Render**: Free tier with webhooks support
- **Heroku**: Classic platform with add-ons

## User Commands

### 查询汇率 (Rate Inquiry)
- `汇率` or `rate` - Display all bank rates
- `计算 5000` or `calc 5000` - Calculate exchange for 5000 CNY

### 排队功能 (Queue System)
- `排队` or `queue` - Join the customer queue
- `位置` or `status` - Check your position
- `离开` or `leave` - Leave the queue

### 汇率预警 (Rate Alerts)
- `预警 4.55` or `alert 4.55` - Set alert when rate ≥ 4.55
- `取消预警` or `cancel alert` - Cancel your alert

## Admin Commands

Only users in `ADMIN_USER_IDS` can use these:
- `下一个` or `next` - Get next customer from queue
- `完成` or `done` - Mark current customer as completed
- `队列` or `queue list` - View full queue

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot access token | Required |
| `LINE_CHANNEL_SECRET` | LINE Bot secret | Required |
| `ADMIN_USER_IDS` | Comma-separated LINE user IDs | Empty |
| `RATE_UPDATE_INTERVAL` | Rate refresh interval (min) | 30 |
| `ALERT_CHECK_INTERVAL` | Alert check interval (min) | 30 |
| `PORT` | Server port | 5000 |

## Project Structure

```
thai-baht-exchange-bot/
├── app.py              # Main Flask LINE Bot application
├── scraper.py          # Multi-bank rate scraper
├── calculator.py       # Exchange calculation & formatting
├── database.py         # SQLite database management
├── queue_manager.py    # Customer queue FIFO logic
├── alerts.py           # Rate alert monitoring
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── README.md          # This file
```

## How It Works

1. **Background Tasks**: 
   - Scraper fetches rates every 30 minutes
   - Alert checker runs every 30 minutes
   
2. **Queue System**:
   - Customers join queue via LINE
   - Admin processes in FIFO order
   - Automatic notifications at each step

3. **Rate Alerts**:
   - Users set target rate
   - System checks periodically
   - Push notification when triggered

## Troubleshooting

### Bot doesn't respond
- Check webhook is set correctly in LINE Console
- Verify server is publicly accessible
- Check logs for errors

### Getting your LINE User ID
1. Send any message to the bot
2. Check the application logs
3. You'll see: `Message from YourName (U1234567890abcdef)`
4. Copy the user ID and add to `.env`

### Rates not updating
- Check scraper.py logs for errors
- Some banks have WAF protection (using fallback rates)
- For production, consider Selenium/Playwright for protected sites

## Notes

- Currently using **fallback rates** for WAF-protected sites (K-Bank, Krungsri, Bangkok Bank)
- For production, implement browser automation (Selenium/Playwright) for these sites
- SuperRich API may require additional headers - monitor logs

## License

MIT

## Support

For issues or questions, contact the administrator.
