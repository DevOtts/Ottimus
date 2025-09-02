# 🚀 Deployment Guide - Telegram to n8n Integration

This guide covers all deployment methods for the Telegram to n8n Integration Docker container.

## 📋 Prerequisites

- ✅ **Completed local authentication** (session.session file exists)
- ✅ **Environment variables configured** (see .env.example)
- ✅ **Docker and Docker Compose installed**
- ✅ **Repository**: https://github.com/DevOtts/Ottimus

## 🐳 Local Docker Deployment

### Method 1: Docker Compose (Recommended)

**Quick Start:**
```bash
# Clone the repository
git clone https://github.com/DevOtts/Ottimus.git
cd Ottimus/telegram-n8n-integration

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up --build

# Run in background (detached)
docker-compose up -d --build
```

**Environment Configuration (.env file):**
```bash
# Your Telegram API credentials from https://my.telegram.org
TELEGRAM_API_ID=16952372
TELEGRAM_API_HASH=6993367159138785c01a9a4d24ad3ee9
TELEGRAM_PHONE=+5541999193736

# Your n8n webhook URL
N8N_WEBHOOK_URL=https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook

# Your specific channel whitelist
TELEGRAM_WHITELIST_CHATS=-1001774144094
```

**Container Management:**
```bash
# View logs
docker-compose logs -f

# Stop the service
docker-compose down

# Restart after changes
docker-compose up -d --build

# Check container status
docker-compose ps
```

### Method 2: Manual Docker Commands

```bash
# Build the image
docker build -t telegram-n8n-listener .

# Create named volume for session persistence
docker volume create telegram_session_data

# Run the container
docker run -d \
  --name telegram-n8n-listener \
  --restart unless-stopped \
  -v telegram_session_data:/app/data \
  -e TELEGRAM_API_ID=16952372 \
  -e TELEGRAM_API_HASH=6993367159138785c01a9a4d24ad3ee9 \
  -e TELEGRAM_PHONE=+5541999193736 \
  -e N8N_WEBHOOK_URL=https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook \
  -e TELEGRAM_WHITELIST_CHATS=-1001774144094 \
  telegram-n8n-listener

# View logs
docker logs -f telegram-n8n-listener

# Stop container
docker stop telegram-n8n-listener

# Remove container
docker rm telegram-n8n-listener
```

## 🌐 VPS Deployment

### Method 1: Portainer UI Deployment (Recommended for VPS)

#### Step 1: Access Portainer
- Open your VPS Portainer interface: `http://your-vps-ip:9000`
- Login to Portainer dashboard

#### Step 2: Deploy via Repository (Easiest)

1. **Create Stack**:
   - Go to **"Stacks"** → **"Add Stack"**
   - **Name**: `telegram-n8n-integration`
   - **Build method**: **"Repository"**

2. **Repository Configuration**:
   ```
   Repository URL: https://github.com/DevOtts/Ottimus
   Compose path: telegram-n8n-integration/docker-compose.yml
   ```

3. **Environment Variables**:
   ```
   TELEGRAM_API_ID=16952372
   TELEGRAM_API_HASH=6993367159138785c01a9a4d24ad3ee9
   TELEGRAM_PHONE=+5541999193736
   N8N_WEBHOOK_URL=https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook
   TELEGRAM_WHITELIST_CHATS=-1001774144094
   ```

4. **Deploy Stack**:
   - Click **"Deploy the stack"**
   - Portainer will clone the repo, build, and start your container

#### Step 3: Deploy via Web Editor (Alternative)

1. **Create Stack**:
   - Go to **"Stacks"** → **"Add Stack"**
   - **Name**: `telegram-n8n-integration`
   - **Build method**: **"Web editor"**

2. **Paste Docker Compose Configuration**:
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

3. **Set Environment Variables** (same as above)
4. **Deploy**

#### Step 4: Initial Authentication (First deployment only)

⚠️ **Important**: First deployment requires interactive authentication:

1. **Container will fail** on first run (needs authentication)
2. **Access container console** in Portainer:
   - Go to **"Containers"** → **telegram-n8n-listener** → **"Console"**
   - **Connect** and run: `python main.py`
   - **Enter SMS code and 2FA password** when prompted
3. **Restart container** - now it will use the session file automatically

#### Step 5: Monitor and Manage

- **View Logs**: Containers → telegram-n8n-listener → Logs
- **Restart**: Containers → telegram-n8n-listener → Restart
- **Update**: Stacks → telegram-n8n-integration → "Update the stack"

### Method 2: VPS Terminal Deployment

#### Option A: Using Git Repository

```bash
# Connect to your VPS
ssh user@your-vps-ip

# Clone the repository
git clone https://github.com/DevOtts/Ottimus.git
cd Ottimus/telegram-n8n-integration

# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
# Add your credentials (same as local deployment)

# Deploy with Docker Compose
docker-compose up -d --build

# View logs
docker-compose logs -f
```

#### Option B: Manual Docker Commands on VPS

```bash
# Connect to your VPS
ssh user@your-vps-ip

# Create a directory for the project
mkdir -p /opt/telegram-n8n-integration
cd /opt/telegram-n8n-integration

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py discover_chats.py ./
COPY .env.example ./

RUN mkdir -p /app/data

VOLUME ["/app/data"]

CMD ["python", "main.py"]
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
telethon==1.40.0
requests==2.31.0
python-dotenv==1.0.0
EOF

# Download application files (you'll need to copy main.py and discover_chats.py)
# Option 1: Use wget/curl to download from raw GitHub files
# Option 2: Copy files via scp from local machine
# Option 3: Use the repository method above instead

# Build and run
docker build -t telegram-n8n-listener .
docker run -d \
  --name telegram-n8n-listener \
  --restart unless-stopped \
  -v telegram_session_data:/app/data \
  -e TELEGRAM_API_ID=16952372 \
  -e TELEGRAM_API_HASH=6993367159138785c01a9a4d24ad3ee9 \
  -e TELEGRAM_PHONE=+5541999193736 \
  -e N8N_WEBHOOK_URL=https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook \
  -e TELEGRAM_WHITELIST_CHATS=-1001774144094 \
  telegram-n8n-listener
```

## 🔧 Management Commands

### Container Operations

```bash
# Check container status
docker ps | grep telegram-n8n-listener

# View real-time logs
docker logs -f telegram-n8n-listener

# Restart container
docker restart telegram-n8n-listener

# Stop container
docker stop telegram-n8n-listener

# Remove container (keeps volume data)
docker rm telegram-n8n-listener

# Check volume data
docker volume ls
docker volume inspect telegram_session_data
```

### Docker Compose Operations

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f telegram-n8n-listener

# Restart service
docker-compose restart

# Stop all services
docker-compose down

# Start services
docker-compose up -d

# Rebuild and restart
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

### Update Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Or in Portainer: Stacks → Update the stack
```

## 🛠️ Troubleshooting

### Container Won't Start

```bash
# Check container logs
docker logs telegram-n8n-listener

# Common issues:
# 1. Missing environment variables
# 2. Authentication needed (first run)
# 3. Invalid credentials
```

### Authentication Issues

```bash
# First deployment needs interactive authentication
# Access container console and run:
docker exec -it telegram-n8n-listener python main.py

# Or in Portainer: Console → Connect → python main.py
```

### Session Persistence Issues

```bash
# Check if volume exists
docker volume ls | grep telegram_session_data

# Inspect volume
docker volume inspect telegram_session_data

# Check if session file exists
docker exec -it telegram-n8n-listener ls -la /app/data/
```

### Port and Network Issues

```bash
# Check if container is running
docker ps | grep telegram-n8n-listener

# Check container networking
docker network ls
docker network inspect telegram-n8n-integration_telegram-network
```

## 📊 Expected Success Logs

When everything is working correctly, you should see:

```
INFO - Whitelist configured for 1 chats: [-1001774144094]
INFO - Starting Telegram to n8n Integration...
INFO - Docker deployment - Session storage: /app/data/session.session
INFO - Connecting to Telegram API with phone: +5541999193736
INFO - Connection to 149.154.175.58:443/TcpFull complete!
INFO - Successfully connected to Telegram!
INFO - Webhook endpoint: https://webhookn8n.otimiza.ai/webhook/ottimus-telegram-webhook
INFO - Monitoring 1 whitelisted chats: [-1001774144094]
INFO - Listening for messages... (Press Ctrl+C to stop)

# When messages arrive:
INFO - New message from channel -1001774144094: #NEIROETH/USDT (Short📉, x20)...
INFO - Successfully sent to n8n: HTTP 200
```

## 🔒 Security Best Practices

### Environment Variables
- ✅ Never commit `.env` files to Git
- ✅ Use Portainer's environment variable management for production
- ✅ Rotate API credentials if compromised

### Network Security
- ✅ Use HTTPS for n8n webhook URLs
- ✅ Consider firewall rules for VPS
- ✅ Monitor container logs for unusual activity

### Access Control
- ✅ Whitelist only necessary chat IDs
- ✅ Regular review of monitored channels
- ✅ Use strong VPS authentication (SSH keys)

## 📞 Support

### Repository
- **Source Code**: https://github.com/DevOtts/Ottimus
- **Issues**: Report problems via GitHub Issues

### Documentation
- **Telegram API**: https://docs.telethon.dev/
- **Docker**: https://docs.docker.com/
- **Portainer**: https://documentation.portainer.io/

---

**🎉 Your Telegram to n8n integration is now ready for production deployment!**

Choose the deployment method that best fits your workflow:
- **Local Development**: Docker Compose
- **VPS with UI**: Portainer (recommended)
- **VPS Command Line**: Docker commands or Git + Compose
