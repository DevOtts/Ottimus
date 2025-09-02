# Telegram to n8n Integration

## 📋 Project Overview

This project creates a minimal Python application that listens to Telegram messages from groups where your personal user is a member and forwards them to n8n workflows via webhooks. The solution uses Telethon (Telegram's Python library) and is designed to run in Docker containers on your VPS with Portainer management.

### Business Purpose
- **Real-time Message Processing**: Capture Telegram group messages as they arrive
- **Workflow Automation**: Trigger n8n workflows based on Telegram activity
- **Personal Integration**: Monitor groups you're already a member of without requiring bot permissions
- **Self-hosted Deployment**: Run continuously on your own VPS with Docker

## 🏗️ Architecture Overview

```
Telegram Groups → Telethon Client → Webhook → n8n Workflow
     ↑                ↑              ↑           ↑
Personal User    Docker Container  HTTP POST   Automation
  Membership      (VPS/Portainer)   Request      Logic
```

## 📁 Project Structure

```
telegram-n8n-integration/
├── Dockerfile                # Docker container configuration
├── docker-compose.yml        # Docker Compose orchestration
├── main.py                  # Complete application (single file)
├── discover_chats.py        # Chat ID discovery utility
├── requirements.txt         # Python dependencies
├── session.session         # Telegram authentication (generated after first auth)
├── .env.example            # Template for local environment variables
├── .gitignore              # Git ignore patterns
└── README.md               # This file
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
1. **First time**: You'll be prompted for verification code from Telegram SMS
2. **If you have 2FA enabled**: You'll also be prompted for your Two-Step Verification password
3. **Creates**: `session.session` file (keep this for deployment!)
4. **Shows**: All incoming messages with their chat IDs in logs
5. **Press Ctrl+C** to stop after you see some messages

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
INFO - Docker deployment - Session storage: /app/data/session.session
INFO - Successfully connected to Telegram!
INFO - Webhook endpoint: https://your-n8n.com/webhook/telegram
INFO - Monitoring 3 whitelisted chats: [-1001234567890, 123456789, -1001987654321]
INFO - Listening for messages... (Press Ctrl+C to stop)
INFO - New message from channel -1001234567890: Test message
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

## 🐳 Docker Deployment

### Local Docker Testing

#### Prerequisites
- Docker and Docker Compose installed
- Completed local authentication (have session.session file)
- Environment variables configured in .env

#### Build and Run with Docker Compose
```bash
# Make sure you're in the telegram-n8n-integration directory
cd telegram-n8n-integration

# Build and start the container
docker-compose up --build

# Run in background (detached mode)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Manual Docker Commands
```bash
# Build the image
docker build -t telegram-n8n-listener .

# Run with volume and environment variables
docker run -d \
  --name telegram-n8n-listener \
  --restart unless-stopped \
  -v telegram_session_data:/app/data \
  -e TELEGRAM_API_ID=${TELEGRAM_API_ID} \
  -e TELEGRAM_API_HASH=${TELEGRAM_API_HASH} \
  -e TELEGRAM_PHONE=${TELEGRAM_PHONE} \
  -e N8N_WEBHOOK_URL=${N8N_WEBHOOK_URL} \
  -e TELEGRAM_WHITELIST_CHATS=${TELEGRAM_WHITELIST_CHATS} \
  telegram-n8n-listener
```

### VPS Deployment with Portainer

#### Prerequisites
- ✅ VPS with Docker and Portainer installed
- ✅ Local testing completed successfully
- ✅ Session file created locally (will be recreated in container)

#### Method 1: Deploy via Portainer UI (Recommended)

1. **Access Portainer**:
   - Open your VPS Portainer interface (usually `http://your-vps-ip:9000`)
   - Login to Portainer dashboard

2. **Create Stack**:
   - Go to **"Stacks"** → **"Add Stack"**
   - **Name**: `telegram-n8n-integration`
   - **Build method**: Choose **"Web editor"**

3. **Paste Docker Compose Configuration**:
   ```yaml
   version: '3.8'
   services:
     telegram-n8n-listener:
       build: .
       container_name: telegram-n8n-listener
       restart: unless-stopped
       volumes:
         - telegram_session_data:/app/data
       environment:
         - TELEGRAM_API_ID=${TELEGRAM_API_ID}
         - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
         - TELEGRAM_PHONE=${TELEGRAM_PHONE}
         - N8N_WEBHOOK_URL=${N8N_WEBHOOK_URL}
         - TELEGRAM_WHITELIST_CHATS=${TELEGRAM_WHITELIST_CHATS}
       networks:
         - telegram-network
   volumes:
     telegram_session_data:
   networks:
     telegram-network:
   ```

4. **Set Environment Variables**:
   - In the **"Environment variables"** section, add:
   ```
   TELEGRAM_API_ID=16952372
   TELEGRAM_API_HASH=6993367159138785c01a9a4d24ad3ee9
   TELEGRAM_PHONE=+5541999193736
   N8N_WEBHOOK_URL=https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook
   TELEGRAM_WHITELIST_CHATS=-1001774144094
   ```

5. **Deploy Stack**:
   - Click **"Deploy the stack"**
   - Portainer will build and start your container

6. **Initial Authentication** (First deployment only):
   - Container will fail on first run (needs authentication)
   - Go to **"Containers"** → **telegram-n8n-listener** → **"Console"**
   - **Connect** and run: `python main.py`
   - **Enter SMS code and 2FA password** when prompted
   - **Exit** and restart container - it will now use the session file automatically

7. **Monitor**:
   - Go to **"Containers"** to see your running service
   - Click on the container to view logs and manage it

#### Method 2: Deploy via Git Repository

1. **Prepare Repository**:
   ```bash
   # Create repository with Docker files
   git add Dockerfile docker-compose.yml
   git commit -m "Add Docker deployment configuration"
   git push
   ```

2. **Deploy in Portainer**:
   - **Stacks** → **"Add Stack"** → **"Repository"**
   - **Repository URL**: Your GitHub repository URL
   - **Compose path**: `docker-compose.yml`
   - **Environment variables**: Set as above
   - **Deploy**

### Container Management

#### View Logs
```bash
# Via docker-compose
docker-compose logs -f

# Via docker commands
docker logs -f telegram-n8n-listener

# In Portainer: Containers → telegram-n8n-listener → Logs
```

#### Update Deployment
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build -d

# In Portainer: Stacks → telegram-n8n-integration → "Update the stack"
```

#### Manage Container
```bash
# Stop
docker-compose down

# Start
docker-compose up -d

# Restart
docker-compose restart

# In Portainer: Use the container management interface
```

## 🛠️ Troubleshooting

### Authentication Problems
```bash
# ❌ "Invalid phone number" 
# ✅ Fix: Include country code: +5511999888777

# ❌ "Invalid API credentials"
# ✅ Fix: Double-check API ID and API Hash from my.telegram.org

# ❌ App asks for password after SMS code
# ✅ Fix: You have Two-Factor Authentication enabled in Telegram
# ✅ Enter your Two-Step Verification password (the one YOU set up)
# ✅ Check: Telegram Settings → Privacy and Security → Two-Step Verification

# ❌ "Invalid password" or forgot 2FA password
# ✅ Fix Option 1: Reset 2FA password via email (if you set recovery email)
# ✅ Fix Option 2: Temporarily disable 2FA in Telegram for setup
# ✅ Remember: You can re-enable 2FA after session.session is created

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

### Docker Issues
```bash
# ❌ Docker build fails
# ✅ Fix: Ensure all files (Dockerfile, requirements.txt, main.py) exist
# ✅ Check: Docker is running and you have sufficient permissions

# ❌ Container exits immediately
# ✅ Fix: Check container logs: docker logs telegram-n8n-listener
# ✅ Most likely: Environment variables not set or authentication needed

# ❌ Session not persisting across container restarts
# ✅ Fix: Ensure volume is properly mounted: telegram_session_data:/app/data
# ✅ Check: Volume exists: docker volume ls
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

## 🛡️ Security Considerations

### Credential Management
- ✅ Never commit `.env` to repository
- ✅ Use Portainer's environment variables for production
- ✅ Rotate API credentials if compromised

### Access Control
- ✅ **Whitelist Protection**: Only configured chat IDs trigger webhooks
- ✅ **Privacy by Design**: Non-whitelisted messages are discarded
- ✅ **Granular Control**: Specify exactly which chats to monitor
- ✅ **Default Security**: Empty whitelist means NO messages forwarded (fail-safe)

### Network Security
- ✅ n8n webhook should use HTTPS
- ✅ Container isolation via Docker networks
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

### **Docker Test:**
- [ ] 🐳 Build Docker image successfully: `docker build -t telegram-n8n-listener .`
- [ ] 🚀 Run with docker-compose: `docker-compose up --build`
- [ ] 📊 Verify container logs show successful connection
- [ ] 🔄 Test container restart: session persists

## 📞 Support & Resources

### Documentation Links
- [Telethon Documentation](https://docs.telethon.dev/)
- [Telegram API Documentation](https://core.telegram.org/api)
- [n8n Webhook Documentation](https://docs.n8n.io/integrations/trigger-nodes/webhook/)
- [Docker Documentation](https://docs.docker.com/)
- [Portainer Documentation](https://documentation.portainer.io/)

### Technical Requirements
- **Python Version**: 3.9+ required (including Python 3.13+ support)
- **Container Platform**: Docker with docker-compose support
- **Dependencies**: Telethon 1.40.0, requests 2.31.0, python-dotenv 1.0.0
- **Session Storage**: Docker volume-mounted (`/app/data/session.session`)

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

# Docker development
docker-compose up --build         # Test in container
docker-compose logs -f            # View container logs
```

### Git Workflow
```bash
# After successful local testing
git add session.session           # IMPORTANT: Include session file
git add Dockerfile docker-compose.yml
git add .
git commit -m "Update Docker implementation"
git push

# Deploy via Portainer using repository method
```

## 🎉 Success Indicators

You know everything is working when you see:

**✅ Local Success:**
```
INFO - Starting Telegram to n8n Integration...
INFO - Docker deployment - Session storage: /app/data/session.session
INFO - Successfully connected to Telegram!
INFO - Webhook endpoint: https://your-n8n.com/webhook/telegram
INFO - Monitoring 1 whitelisted chats: [-1001774144094]
INFO - Listening for messages... (Press Ctrl+C to stop)
INFO - New message from channel -1001774144094: #NEUROETH/USDT (Short📉, x20)...
INFO - Successfully sent to n8n: HTTP 200
```

**✅ Docker Success:**
```
telegram-n8n-listener    | INFO - Starting Telegram to n8n Integration...
telegram-n8n-listener    | INFO - Docker deployment - Session storage: /app/data/session.session
telegram-n8n-listener    | INFO - Successfully connected to Telegram!
telegram-n8n-listener    | INFO - Listening for messages...
```

**✅ n8n Success:**
- Webhook receives JSON payload
- Workflow executes successfully
- No errors in n8n execution logs

**✅ Production Success (Portainer):**
- Container shows "running" status in Portainer
- Logs show successful Telegram connections
- Messages flowing from your specific channel to n8n

---

*Ready to connect your Telegram channel to n8n automation with Docker! 🐳🚀*