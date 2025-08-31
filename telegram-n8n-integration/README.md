# Telegram to n8n Integration

## 📋 Project Overview

This project creates a minimal Python application that listens to Telegram messages from groups where your personal user is a member and forwards them to n8n workflows via webhooks. The solution uses Telethon (Telegram's Python library) and is designed to run continuously on Render.com.

### Business Purpose
- **Real-time Message Processing**: Capture Telegram group messages as they arrive
- **Workflow Automation**: Trigger n8n workflows based on Telegram activity
- **Personal Integration**: Monitor groups you're already a member of without requiring bot permissions
- **Cloud Deployment**: Run continuously without local infrastructure

## 🏗️ Architecture Overview

```
Telegram Groups → Telethon Client → Webhook → n8n Workflow
     ↑                ↑              ↑           ↑
Personal User    Python App     HTTP POST   Automation
  Membership    (Render.com)    Request      Logic
```

## 📁 Project Structure

```
telegram-n8n-integration/
├── main.py                # Complete application (single file)
├── discover_chats.py      # Chat ID discovery utility
├── requirements.txt       # Python dependencies (2 packages)
├── render.yaml           # Render.com deployment config
├── session.session       # Telegram authentication (generated after first auth)
├── .env.example          # Template for local environment variables
├── .gitignore            # Git ignore patterns
└── README.md             # This file
```

## 🚀 Quick Start Guide

### Step 1: Get Telegram API Credentials

1. **Visit**: https://my.telegram.org
2. **Login** with your Telegram phone number (include country code: `+5511999888777`)
3. **Enter verification code** sent to your Telegram app
4. **Click "API Development Tools"**
5. **Fill out the form**:
   - **App title**: `n8n-telegram-listener` (or any name)
   - **Short name**: `n8nlistener` (no spaces)
   - **Platform**: Select `Other`
   - Leave other fields as default
6. **Click "Create Application"**
7. **Save these values** (you'll need them):
   - **API ID** (integer, e.g., `1234567`)
   - **API Hash** (long alphanumeric string)

### Step 2: Set Up n8n Webhook

1. **Open your n8n instance**
2. **Create new workflow**
3. **Add "Webhook" trigger node**
4. **Configure**:
   - **HTTP Method**: POST
   - **Path**: `/webhook/telegram` (or your choice)
   - **Authentication**: None
5. **Copy the webhook URL** (e.g., `https://your-n8n.com/webhook/telegram`)

### Step 3: Local Environment Setup

#### Create Virtual Environment
```bash
# Clone or navigate to the project directory
cd telegram-n8n-integration

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
# Copy template to create local environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or code .env, or vim .env
```

**Replace the template values in `.env` with your real credentials:**
```bash
# Telegram API Credentials from my.telegram.org
TELEGRAM_API_ID=1234567                    # Your actual API ID
TELEGRAM_API_HASH=abcdef1234567890abcdef   # Your actual API Hash

# Your phone number with country code
TELEGRAM_PHONE=+5511999888777              # Your actual phone

# Your n8n webhook URL
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/telegram

# Leave empty initially for chat discovery
TELEGRAM_WHITELIST_CHATS=
```

### Step 4: First Run - Authentication & Chat Discovery

#### Initial Authentication
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application for first-time authentication
python main.py
```

**What happens:**
1. **First time**: You'll be prompted for verification code from Telegram
2. **Creates**: `session.session` file (keep this for deployment!)
3. **Shows**: All incoming messages with their chat IDs in logs
4. **Press Ctrl+C** to stop after you see some messages

#### Discover Chat IDs

**Method 1: Use the discovery script (Recommended)**
```bash
# Run the chat discovery utility
python discover_chats.py
```

This will show you all your chats with their IDs:
```
🔍 Discovering your chats and their IDs:
============================================================

📢 GROUPS:
  My Awesome Group                         | ID: -1001234567890
  Work Team Chat                           | ID: -1001987654321

📺 CHANNELS:
  News Channel                             | ID: -1001111111111

👤 DIRECT MESSAGES: 25 total (showing first 5)
  John Doe                                 | ID: 123456789
  Jane Smith                               | ID: 987654321

============================================================
📋 Example whitelist configuration:
TELEGRAM_WHITELIST_CHATS=-1001234567890,-1001987654321,123456789
```

**Method 2: Use application logs**
With empty whitelist, the main app will show logs like:
```
INFO - New message from group -1001234567890: Hello everyone!
INFO - New message from DM 123456789: Hi there!
```

### Step 5: Configure Whitelist & Test

#### Update Environment Configuration
```bash
# Edit .env file again
nano .env

# Add the chat IDs you want to monitor (comma-separated)
TELEGRAM_WHITELIST_CHATS=-1001234567890,123456789,-1001987654321
```

#### Test Webhook Delivery
```bash
# Restart the application
python main.py
```

**Send a test message** in one of your whitelisted chats. You should see:
```
INFO - Starting Telegram to n8n Integration...
INFO - Successfully connected to Telegram!
INFO - Webhook endpoint: https://your-n8n.com/webhook/telegram
INFO - Monitoring 3 whitelisted chats
INFO - Listening for messages... (Press Ctrl+C to stop)
INFO - New message from group -1001234567890: Test message
INFO - Successfully sent to n8n: HTTP 200
```

✅ **Success!** Your integration is working when you see "HTTP 200" responses.

## 🔧 Advanced Configuration

### Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TELEGRAM_API_ID` | ✅ | API ID from my.telegram.org | `1234567` |
| `TELEGRAM_API_HASH` | ✅ | API Hash from my.telegram.org | `abcdef123...` |
| `TELEGRAM_PHONE` | ✅ | Phone with country code | `+5511999888777` |
| `N8N_WEBHOOK_URL` | ✅ | n8n webhook endpoint | `https://n8n.com/webhook/telegram` |
| `TELEGRAM_WHITELIST_CHATS` | 🔶 | Comma-separated chat IDs | `-1001234567890,123456789` |

### Chat ID Format Reference
- **Group Chat**: `-1001234567890` (negative, starts with -100)
- **Direct Message**: `123456789` (positive)
- **Channel**: `-1001987654321` (negative, starts with -100)

### Webhook Payload Format

The application sends JSON data to your n8n webhook with this structure:
```json
{
  "message": "The actual message text",
  "chat_id": -1001234567890,
  "sender_id": 123456789,
  "date": "2024-01-15T14:30:00.000Z",
  "is_group": true,
  "is_channel": false
}
```

## 🛠️ Troubleshooting

### Authentication Problems
```bash
# ❌ "Invalid phone number" 
# ✅ Fix: Include country code: +5511999888777

# ❌ "Invalid API credentials"
# ✅ Fix: Double-check API ID and API Hash from my.telegram.org

# ❌ Repeated auth requests
# ✅ Fix: Make sure session.session file exists and is readable
```

### Environment Issues
```bash
# ❌ "Missing required environment variables" (even when .env exists)
# ✅ Fix 1: Make sure python-dotenv is installed: pip install python-dotenv
# ✅ Fix 2: Check .env file has all required vars (no typos in names)
# ✅ Fix 3: Ensure .env is in the same directory as main.py

# ❌ "Invalid whitelist format"
# ✅ Fix: Use comma-separated integers: -1001234567890,123456789
```

### Python Compatibility Issues
```bash
# ❌ "ModuleNotFoundError: No module named 'imghdr'" (Python 3.13+)
# ✅ Fix: Upgrade Telethon to 1.40.0+ which supports Python 3.13
# Run: pip install telethon --upgrade

# ❌ Virtual environment issues with Python 3.13
# ✅ Fix: Recreate virtual environment with the upgraded Telethon:
# python3 -m venv venv --clear
# source venv/bin/activate
# pip install -r requirements.txt
```

### Webhook Problems
```bash
# ❌ "Webhook timeout error"
# ✅ Fix: Check n8n URL is accessible and workflow is ACTIVE

# ❌ "Webhook error: HTTP 404"
# ✅ Fix: Verify n8n webhook path is correct

# ❌ "Connection error"
# ✅ Fix: Check internet connection and n8n instance is running
```

### No Messages Being Forwarded
```bash
# ❌ Empty logs, no activity
# ✅ Check: Are you a member of the groups you're monitoring?
# ✅ Check: Is whitelist configured correctly?
# ✅ Check: Send a test message in the whitelisted chat

# ❌ "Message from non-whitelisted chat - discarding"
# ✅ Fix: Add the chat ID to your whitelist or leave whitelist empty for testing
```

## 🌐 Deployment to Render.com

### Prerequisites for Deployment
- ✅ Local testing successful
- ✅ `session.session` file created
- ✅ All environment variables known

### Deployment Steps

1. **Create GitHub Repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial Telegram to n8n integration"
   git remote add origin https://github.com/your-username/telegram-n8n-integration.git
   git push -u origin main
   ```

2. **Deploy on Render.com**:
   - Go to [https://dashboard.render.com/](https://dashboard.render.com/)
   - Click **"New +"** → **"Background Worker"**
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables in Render**:
   Set the same variables from your `.env` file:
   - `TELEGRAM_API_ID` → Your API ID
   - `TELEGRAM_API_HASH` → Your API Hash
   - `TELEGRAM_PHONE` → Your phone number
   - `N8N_WEBHOOK_URL` → Your n8n webhook URL
   - `TELEGRAM_WHITELIST_CHATS` → Your chat IDs

4. **Deploy**: Click "Create Web Service"

The `render.yaml` file contains all deployment configuration:
```yaml
services:
  - type: worker
    name: telegram-n8n-listener
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    envVars:
      - key: TELEGRAM_API_ID
        sync: false
      - key: TELEGRAM_API_HASH
        sync: false
      - key: TELEGRAM_PHONE
        sync: false
      - key: N8N_WEBHOOK_URL
        sync: false
      - key: TELEGRAM_WHITELIST_CHATS
        sync: false
```

## 🔍 Monitoring & Logs

### Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Run with verbose output
python main.py

# Check what's happening
tail -f /path/to/logs  # if you configure file logging
```

### Production (Render.com)
- **Monitor**: Render dashboard logs
- **Check**: Service health and uptime
- **Debug**: Environment variable configuration

## 🛡️ Security Considerations

### Credential Management
- ✅ Never commit `.env` to repository
- ✅ Use Render's environment variables for production
- ✅ Rotate API credentials if compromised

### Access Control
- ✅ **Whitelist Protection**: Only configured chat IDs trigger webhooks
- ✅ **Privacy by Design**: Non-whitelisted messages are discarded
- ✅ **Granular Control**: Specify exactly which chats to monitor
- ✅ **Default Security**: Empty whitelist means NO messages forwarded (fail-safe)

### Network Security
- ✅ n8n webhook should use HTTPS
- 🔶 Consider implementing webhook authentication/signatures
- 🔶 Monitor for unusual traffic patterns

## 📊 Testing Checklist

### **Environment Setup:**
- [ ] ✅ Virtual environment created and activated
- [ ] ✅ Dependencies installed (`pip install -r requirements.txt`)
- [ ] 📝 `.env` configured with real credentials
- [ ] 🔗 n8n webhook URL ready

### **Authentication Test:**
- [ ] 🔐 Run `python main.py` (enter verification code when prompted)
- [ ] 📄 `session.session` file created
- [ ] 📡 "Successfully connected to Telegram!" message shown

### **Chat Discovery:**
- [ ] 🔍 Run `python discover_chats.py` OR
- [ ] 👀 Check logs from main app with empty whitelist
- [ ] 📋 Copy chat IDs you want to monitor

### **Whitelist Configuration:**
- [ ] ✏️ Add chat IDs to `TELEGRAM_WHITELIST_CHATS` in `.env`
- [ ] 🔄 Restart application
- [ ] ✅ See "Monitoring X whitelisted chats" message

### **Webhook Test:**
- [ ] 📨 Send test message in whitelisted chat
- [ ] 📊 Check logs: "Successfully sent to n8n: HTTP 200"
- [ ] 🎯 Verify n8n workflow triggered

## 📞 Support & Resources

### Documentation Links
- [Telethon Documentation](https://docs.telethon.dev/)
- [Telegram API Documentation](https://core.telegram.org/api)
- [n8n Webhook Documentation](https://docs.n8n.io/integrations/trigger-nodes/webhook/)
- [Render.com Documentation](https://render.com/docs)

### Technical Requirements
- **Python Version**: 3.9+ required (including Python 3.13+ support)
- **Platform**: Render.com Background Worker Service  
- **Dependencies**: Telethon 1.40.0, requests 2.31.0, python-dotenv 1.0.0
- **Session Storage**: File-based (`session.session`)

## 🔄 Development Workflow

### Local Development Commands
```bash
# Setup (one-time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Daily development
source venv/bin/activate          # Activate environment
python main.py                    # Run main application
python discover_chats.py          # Discover chat IDs

# Testing
TELEGRAM_WHITELIST_CHATS="" python main.py  # Run without whitelist
```

### Git Workflow
```bash
# After successful local testing
git add session.session           # IMPORTANT: Include session file
git add .
git commit -m "Update implementation"
git push

# Render.com will auto-deploy on push
```

## 🎉 Success Indicators

You know everything is working when you see:

**✅ Local Success:**
```
INFO - Starting Telegram to n8n Integration...
INFO - Successfully connected to Telegram!
INFO - Webhook endpoint: https://your-n8n.com/webhook/telegram
INFO - Monitoring 3 whitelisted chats
INFO - Listening for messages... (Press Ctrl+C to stop)
INFO - New message from group -1001234567890: Hello world!
INFO - Successfully sent to n8n: HTTP 200
```

**✅ n8n Success:**
- Webhook receives JSON payload
- Workflow executes successfully
- No errors in n8n execution logs

**✅ Production Success:**
- Render service shows "Running" status
- Logs show successful connections
- Messages flowing from Telegram to n8n

---

*Ready to connect your Telegram groups to n8n automation! 🚀*
