# 🚀 Deployment Guide - Telegram to n8n Integration

Simple deployment guide for the Telegram to n8n Integration service.

## ⚠️ Important: Docker Swarm Limitation

**Portainer Stacks use Docker Swarm, which has networking limitations that prevent Telegram connectivity.**

**✅ Recommended**: Use VPS Direct Deployment (works perfectly)  
**❌ Not Recommended**: Portainer Stacks (Docker Swarm networking issues)

---

## 🎯 Method 1: VPS Direct Deployment (Recommended)

**Best for: Production use, VPS servers, simplicity**

### Prerequisites
- VPS with SSH access
- Python 3.8+
- Your Telegram API credentials

### Quick Setup (5 minutes)

```bash
# 1. SSH to your VPS
ssh root@your-vps-ip

# 2. Create project directory
mkdir telegram-n8n && cd telegram-n8n

# 3. Create virtual environment
python3 -m venv telegram-env
source telegram-env/bin/activate

# 4. Install dependencies
pip install telethon requests python-dotenv

# 5. Create the application
cat > telegram_n8n_integration.py << 'EOF'
#!/usr/bin/env python3
import os, logging, asyncio
from telethon import TelegramClient, events
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
client = TelegramClient('session', 16952372, '6993367159138785c01a9a4d24ad3ee9')

@client.on(events.NewMessage(incoming=True))
async def message_handler(event):
    try:
        message_data = {
            "message": event.raw_text or "",
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "date": event.date.isoformat(),
            "is_group": event.is_group,
            "is_channel": event.is_channel
        }
        
        chat_type = "group" if event.is_group else "channel" if event.is_channel else "DM"
        preview = (message_data["message"][:50] + "...") if len(message_data["message"]) > 50 else message_data["message"]
        logger.info(f"New message from {chat_type} {event.chat_id}: {preview}")
        
        response = requests.post('https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook', 
                               json=message_data, timeout=30)
        logger.info(f"Sent to n8n: HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"Error: {e}")

async def main():
    logger.info("Starting Telegram to n8n Integration...")
    await client.start(phone='+5541999193736')
    logger.info("Connected! Listening for ALL messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# 6. Run and authenticate
python telegram_n8n_integration.py
# Enter SMS code and 2FA when prompted
```

### Auto-Start Service (Optional)

```bash
# Create systemd service
sudo tee /etc/systemd/system/telegram-n8n.service << 'EOF'
[Unit]
Description=Telegram to n8n Integration
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram-n8n
Environment=PATH=/root/telegram-n8n/telegram-env/bin
ExecStart=/root/telegram-n8n/telegram-env/bin/python /root/telegram-n8n/telegram_n8n_integration.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable telegram-n8n.service
sudo systemctl start telegram-n8n.service

# Check status
sudo systemctl status telegram-n8n.service
```

---

## 🐳 Method 2: Docker Compose (Non-Swarm Only)

**Best for: Local development, non-Swarm Docker environments**

### Prerequisites
- Docker & Docker Compose
- **NOT using Docker Swarm/Portainer Stacks**

### Setup

```bash
# 1. Clone repository
git clone https://github.com/DevOtts/Ottimus.git
cd Ottimus/telegram-n8n-integration

# 2. Create environment file
cat > .env << 'EOF'
TELEGRAM_API_ID=16952372
TELEGRAM_API_HASH=6993367159138785c01a9a4d24ad3ee9
TELEGRAM_PHONE=+5541999193736
N8N_WEBHOOK_URL=https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook
TELEGRAM_WHITELIST_CHATS=
EOF

# 3. Deploy
docker-compose up -d --build

# 4. First-run authentication
docker exec -it telegram-n8n-integration_telegram-n8n-listener_1 python main.py
# Enter SMS code and 2FA when prompted

# 5. Restart container
docker-compose restart
```

### Management Commands

```bash
# View logs
docker-compose logs -f

# Stop service
docker-compose down

# Update and restart
git pull && docker-compose up -d --build
```

---

## ❌ Why Portainer Stacks Don't Work

**Portainer Stacks use Docker Swarm mode, which has these limitations:**

- ❌ No `network_mode: host` support (needed for Telegram MTProto)
- ❌ Complex networking that blocks Telegram servers
- ❌ Can't bypass Docker's network isolation
- ❌ Different restart policy requirements

**Result**: Connection timeouts when trying to reach Telegram servers.

---

## 🔧 Configuration

### Telegram API Setup
1. Go to https://my.telegram.org
2. Create an application
3. Get your `API_ID` and `API_HASH`

### Whitelist Configuration
- **Empty whitelist** = Monitors ALL messages (good for testing)
- **Specific chat IDs** = Only monitor those chats
- **Format**: `-1001234567890,123456789` (comma-separated)

### n8n Webhook
Make sure your n8n workflow is:
- ✅ **Active**
- ✅ **Listening** for webhook events
- ✅ **Accessible** from your deployment location

---

## 📊 Success Indicators

When working correctly, you'll see:

```
INFO - Starting Telegram to n8n Integration...
INFO - Connected! Listening for ALL messages...
INFO - New message from channel -1001234567890: Hello world...
INFO - Sent to n8n: HTTP 200
```

---

## 🛠️ Troubleshooting

### Authentication Issues
- **Problem**: No SMS code prompt
- **Solution**: Delete session file and restart

### Connection Timeouts
- **Problem**: Can't connect to Telegram
- **Solution**: Use VPS Direct Deployment instead of Docker

### No Messages Received
- **Problem**: Connected but no messages
- **Solution**: Send test message to yourself, check whitelist config

### n8n Not Receiving
- **Problem**: Messages logged but n8n workflow not triggered
- **Solution**: Check webhook URL, ensure n8n workflow is active

---

## 🎉 Summary

**For Production**: Use **VPS Direct Deployment** - it's simpler and works reliably.

**For Development**: Use **Docker Compose** (not Portainer Stacks).

**Avoid**: Portainer Stacks due to Docker Swarm networking limitations.