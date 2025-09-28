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

# 5. Create and edit environment file
nano .env
# Add your credentials:
# TELEGRAM_API_ID=your_api_id
# TELEGRAM_API_HASH=your_api_hash  
# TELEGRAM_PHONE=your_phone_number
# N8N_WEBHOOK_URL=your_n8n_webhook_url
# TELEGRAM_WHITELIST_CHATS=

# 6. Create the application file
touch telegram_n8n_integration.py

# 7. Copy the enhanced main.py content from this repository
# Method A: If you have git access, clone and copy:
git clone https://github.com/DevOtts/Ottimus.git temp-repo
cp temp-repo/telegram-n8n-integration/main.py telegram_n8n_integration.py
rm -rf temp-repo

# Method B: Or manually copy the content from main.py
# Visit: https://github.com/DevOtts/Ottimus/blob/main/telegram-n8n-integration/main.py
# Copy the entire content and paste it into telegram_n8n_integration.py

# The main.py file includes these enhancements:
# ✅ Reply message support (reply_to_msg_id field)
# ✅ Message ID tracking (message_id field) 
# ✅ Enhanced error handling and logging
# ✅ Comprehensive documentation
# ✅ Docker-compatible session management

# 8. Run and authenticate
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
EnvironmentFile=/root/telegram-n8n/.env
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

### Re-Authentication Required (Common Issue)

**When Telegram asks for authentication again while service is running:**

This happens when:
- Telegram session expires (security measure)
- You see "SendCodeRequest" errors in logs  
- Service keeps failing with authentication errors

**Solution:**
```bash
# 1. Stop the service first
sudo systemctl stop telegram-n8n.service

# 2. Navigate to project directory and activate environment
cd /root/telegram-n8n
source telegram-env/bin/activate

# 3. Clean old session files (important!)
rm -f session.session*

# 4. Run manual authentication
python telegram_n8n_integration.py
# ↑ Enter SMS code when prompted
# ↑ Enter 2FA password if you have it enabled
# ↑ Press Ctrl+C after you see "Successfully connected to Telegram!"

# 5. Restart the service
sudo systemctl start telegram-n8n.service

# 6. Verify it's working
sudo systemctl status telegram-n8n.service
sudo journalctl -u telegram-n8n.service -f
```

### Regular Service Management

When you do some change to the code or .env, you will need to restart the service.

```bash
# Restart the service to reload .env changes
sudo systemctl restart telegram-n8n.service

# Check that it restarted successfully
sudo systemctl status telegram-n8n.service

# Watch the live logs to see it working
sudo journalctl -u telegram-n8n.service -f
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
- **Problem**: No SMS code prompt or "EOF when reading a line" error
- **Solution**: 
  ```bash
  # Stop the service first
  sudo systemctl stop telegram-n8n.service
  
  # Run manually to complete authentication
  cd /root/telegram-n8n
  source telegram-env/bin/activate
  python telegram_n8n_integration.py
  # Enter SMS code when prompted, then Ctrl+C after "Connected!"
  
  # Restart service
  sudo systemctl start telegram-n8n.service
  ```

### Rate Limit Error (165 seconds wait)
- **Problem**: "A wait of 165 seconds is required (caused by SendCodeRequest)"
- **Cause**: Session file path mismatch between Docker and VPS versions
- **Solution**: 
  ```bash
  # Delete old session files and re-authenticate
  sudo systemctl stop telegram-n8n.service
  cd /root/telegram-n8n
  rm -f session.session*
  source telegram-env/bin/activate
  python telegram_n8n_integration.py
  # Complete authentication, then restart service
  sudo systemctl start telegram-n8n.service
  ```

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