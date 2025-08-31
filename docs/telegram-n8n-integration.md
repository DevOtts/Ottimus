# Telegram to n8n Integration Project

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
telethon-listener/
├── main.py              # Core application logic
├── requirements.txt     # Python dependencies
├── render.yaml         # Render.com deployment configuration
├── .env               # Environment variables (local development only)
└── session.session   # Telethon session file (generated after first auth)
```

## 🔧 Technical Requirements

### Prerequisites
- Python 3.8+
- Telegram account with phone number
- Telegram API credentials (api_id, api_hash)
- n8n instance with webhook URL
- GitHub account
- Render.com account

### Dependencies
- `telethon==1.29.1` - Telegram MTProto API client
- `requests` - HTTP library for webhook calls

## 🚀 Implementation Guide

### Step 1: Obtain Telegram API Credentials

1. Navigate to: [https://my.telegram.org](https://my.telegram.org)
2. Log in with your Telegram phone number (include country code: `+55XXXXXXXXX`)
3. Enter the verification code sent to your Telegram app
4. Click **"API Development Tools"**
5. Fill out the application form:
   - **App title**: `n8n-telegram-listener` (or any descriptive name)
   - **Short name**: `n8nlistener` (no spaces)
   - **Platform**: Select `Other`
   - Leave other fields as default
6. Click **"Create Application"**
7. **Save these values securely**:
   - **API ID** (integer, e.g., `1234567`)
   - **API Hash** (long alphanumeric string)

### Step 2: Create Project Files

#### `main.py`
```python
import os
from telethon import TelegramClient, events
import requests
import asyncio

# Environment variables
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")
n8n_webhook = os.getenv("N8N_WEBHOOK_URL")
whitelist_chats = os.getenv("TELEGRAM_WHITELIST_CHATS", "")

# Parse whitelist - convert comma-separated string to list of integers
allowed_chat_ids = []
if whitelist_chats:
    try:
        allowed_chat_ids = [int(chat_id.strip()) for chat_id in whitelist_chats.split(",") if chat_id.strip()]
        print(f"Whitelist configured for {len(allowed_chat_ids)} chats: {allowed_chat_ids}")
    except ValueError as e:
        print(f"Invalid whitelist format: {e}")
        print("Whitelist should be comma-separated chat IDs (e.g., '-1001234567890,123456789')")

# Initialize Telegram client
client = TelegramClient('session', api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """
    Handle incoming messages and forward to n8n webhook (only from whitelisted chats)
    """
    try:
        # Check if chat is whitelisted (if whitelist is configured)
        if allowed_chat_ids and event.chat_id not in allowed_chat_ids:
            print(f"Message from non-whitelisted chat {event.chat_id} - discarding")
            return
        
        # Extract message data
        message_data = {
            "message": event.raw_text,
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "date": event.date.isoformat(),
            "is_group": event.is_group,
            "is_channel": event.is_channel
        }
        
        print(f"New whitelisted message from {event.chat_id}: {event.raw_text[:50]}...")
        
        # Send to n8n webhook
        response = requests.post(
            n8n_webhook, 
            json=message_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"Successfully sent to n8n: {response.status_code}")
        else:
            print(f"Webhook error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error processing message: {e}")

async def main():
    """
    Main application entry point
    """
    print("Starting Telegram listener...")
    
    # Start the client
    await client.start(phone=lambda: phone)
    
    print("Successfully connected to Telegram!")
    print("Listening for messages...")
    
    # Keep the client running
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
```

#### `requirements.txt`
```
telethon==1.29.1
requests==2.31.0
```

#### `render.yaml`
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

### Step 3: Initial Authentication (Critical Step)

**⚠️ Important**: Telethon requires interactive authentication on first run. Since Render.com doesn't support interactive input, you must generate the session file locally first.

#### Local Setup Process:
1. Clone your repository locally
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your credentials:
   ```env
   TELEGRAM_API_ID=your_api_id_here
   TELEGRAM_API_HASH=your_api_hash_here
   TELEGRAM_PHONE=+55XXXXXXXXX
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/telegram
   TELEGRAM_WHITELIST_CHATS=-1001234567890,123456789,-1001987654321
   ```
4. Run locally: `python main.py`
5. Enter the verification code when prompted
6. Once authenticated successfully, a `session.session` file will be created
7. **Commit and push the `session.session` file to your repository**

### Step 4: Deploy to Render.com

1. **Create GitHub Repository**:
   - Push all project files including `session.session`
   - Ensure `.env` is in `.gitignore` (credentials will be set in Render)

2. **Deploy on Render**:
   - Go to [https://dashboard.render.com/](https://dashboard.render.com/)
   - Click **"New +"** → **"Background Worker"**
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**:
   - `TELEGRAM_API_ID` → Your API ID from Step 1
   - `TELEGRAM_API_HASH` → Your API Hash from Step 1
   - `TELEGRAM_PHONE` → Your phone number with country code
   - `N8N_WEBHOOK_URL` → Your n8n webhook endpoint
   - `TELEGRAM_WHITELIST_CHATS` → Comma-separated chat IDs (see "Finding Chat IDs" section below)

4. **Deploy**: Click "Create Web Service"

## 🔍 Finding Chat IDs for Whitelist Configuration

### Method 1: Using the Application Logs (Recommended)

The easiest way to find chat IDs is to temporarily run the application **without** the whitelist configured:

1. **Initial Discovery Run**:
   - Set `TELEGRAM_WHITELIST_CHATS` to empty string or don't set it
   - Run the application locally or check Render logs
   - Send a test message in each group/chat you want to whitelist
   - The logs will show: `New message from {chat_id}: {message_preview}...`

2. **Copy the Chat IDs**:
   - Note down all the chat IDs from the logs
   - Group chats typically have negative IDs (e.g., `-1001234567890`)
   - Direct messages have positive IDs (e.g., `123456789`)

3. **Configure Whitelist**:
   - Set `TELEGRAM_WHITELIST_CHATS=-1001234567890,123456789,-1001987654321`
   - Restart the application

### Method 2: Using Telegram Desktop/Web

1. **For Groups**:
   - Open the group in Telegram Desktop or Web
   - Look at the URL: `https://web.telegram.org/a/#-1001234567890`
   - The number after `#` is your chat ID

2. **For Direct Messages**:
   - Contact [@userinfobot](https://t.me/userinfobot) on Telegram
   - Forward a message from the user you want to whitelist
   - The bot will show the user ID

### Method 3: Using a Temporary Script

Create a temporary script to list all your chats:

```python
import os
from telethon import TelegramClient
import asyncio

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")

client = TelegramClient('session', api_id, api_hash)

async def list_chats():
    await client.start(phone=lambda: phone)
    print("Your chats and their IDs:")
    print("-" * 50)
    
    async for dialog in client.iter_dialogs():
        chat_type = "Group" if dialog.is_group else "Channel" if dialog.is_channel else "User"
        print(f"{chat_type}: {dialog.name} | ID: {dialog.id}")

asyncio.run(list_chats())
```

### Whitelist Configuration Format

- **Format**: Comma-separated chat IDs
- **Example**: `-1001234567890,123456789,-1001987654321`
- **Groups**: Usually negative numbers (e.g., `-1001234567890`)
- **Direct Messages**: Usually positive numbers (e.g., `123456789`)
- **Empty Whitelist**: If not set or empty, ALL messages will be forwarded (not recommended for privacy)

### Security Best Practices for Whitelist

- **Start with Empty Whitelist**: Test with no whitelist to discover chat IDs, then restrict
- **Principle of Least Privilege**: Only whitelist chats you actually need to monitor
- **Regular Review**: Periodically review and update your whitelist
- **Group Management**: Remove chat IDs when you leave groups

## 🔗 n8n Webhook Configuration

### Webhook Setup in n8n:
1. Create new workflow in n8n
2. Add "Webhook" trigger node
3. Configure webhook:
   - **HTTP Method**: POST
   - **Path**: `/webhook/telegram` (or your preferred path)
   - **Authentication**: None (or configure as needed)
4. The webhook will receive JSON data with structure:
   ```json
   {
     "message": "The actual message text",
     "chat_id": -1001234567890,
     "sender_id": 123456789,
     "date": "2024-01-15T14:30:00",
     "is_group": true,
     "is_channel": false
   }
   ```

## 🔍 Monitoring & Troubleshooting

### Common Issues & Solutions

#### Authentication Errors
- **Symptom**: "Invalid phone number" or "Invalid API credentials"
- **Solution**: Verify API ID, API Hash, and phone number format (+country_code)

#### Session File Issues
- **Symptom**: Repeated authentication requests
- **Solution**: Ensure `session.session` file is present in repository and was generated successfully locally

#### Webhook Failures
- **Symptom**: Messages received but n8n not triggered
- **Solution**: 
  - Check n8n webhook URL is correct and accessible
  - Verify n8n workflow is active
  - Check Render logs for HTTP error codes

#### Rate Limiting
- **Symptom**: Messages delayed or missing
- **Solution**: Telegram has rate limits; consider implementing message queuing for high-volume scenarios

#### Whitelist Configuration Issues
- **Symptom**: No messages being forwarded despite activity
- **Solution**: 
  - Check if `TELEGRAM_WHITELIST_CHATS` is properly configured
  - Verify chat IDs are correct (use Method 1 from "Finding Chat IDs" section)
  - Ensure chat IDs are comma-separated without spaces around commas
- **Symptom**: "Invalid whitelist format" error in logs
- **Solution**: 
  - Verify all chat IDs are valid integers
  - Remove any extra characters or spaces
  - Use negative numbers for groups, positive for direct messages

### Logging & Debugging
- **Render Logs**: Available in Render dashboard under your service
- **Local Testing**: Use `.env` file for local development and testing
- **Message Filtering**: Modify the event handler to filter specific groups or message types

## 🛡️ Security Considerations

### Credential Management
- Never commit API credentials to repository
- Use Render's environment variables for production
- Rotate API credentials if compromised

### Access Control
- **Whitelist Protection**: Only configured chat IDs will trigger webhooks
- **Privacy by Design**: Messages from non-whitelisted chats are automatically discarded
- **Granular Control**: Specify exactly which groups and direct messages to monitor
- **Default Security**: Empty whitelist means NO messages are forwarded (fail-safe)
- Be mindful of privacy and data handling regulations when selecting chats to monitor

### Network Security
- n8n webhook should use HTTPS
- Consider implementing webhook authentication/signatures
- Monitor for unusual traffic patterns

## 📊 Performance & Scalability

### Expected Performance
- **Message Volume**: Can handle typical personal group message volumes
- **Latency**: Near real-time forwarding (< 5 seconds typical)
- **Uptime**: Dependent on Render.com service reliability

### Scaling Considerations
- For high-volume scenarios, consider implementing:
  - Message queuing (Redis/RabbitMQ)
  - Database logging for message history
  - Load balancing for multiple webhook endpoints

## 🔄 Maintenance

### Regular Tasks
- Monitor Render logs for errors
- Check n8n webhook endpoint health
- Review message processing accuracy

### Updates & Dependencies
- Keep Telethon updated for security patches
- Monitor Telegram API changes
- Update Python version as needed

## ⚡ Quick Reference

### Essential Environment Variables
```bash
# Required
TELEGRAM_API_ID=1234567
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+5511999888777
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/telegram

# Security (Highly Recommended)
TELEGRAM_WHITELIST_CHATS=-1001234567890,123456789,-1001987654321
```

### Chat ID Examples
- **Group Chat**: `-1001234567890` (negative, starts with -100)
- **Direct Message**: `123456789` (positive)
- **Channel**: `-1001987654321` (negative, starts with -100)

### Testing Checklist
- [ ] Local authentication completed successfully
- [ ] Session file generated and committed
- [ ] Environment variables configured in Render
- [ ] Test message sent to whitelisted chat
- [ ] n8n webhook receives message data
- [ ] Non-whitelisted chats are properly ignored

## 📞 Support & Resources

### Documentation Links
- [Telethon Documentation](https://docs.telethon.dev/)
- [Telegram API Documentation](https://core.telegram.org/api)
- [n8n Webhook Documentation](https://docs.n8n.io/integrations/trigger-nodes/webhook/)
- [Render.com Documentation](https://render.com/docs)

### Troubleshooting Resources
- Render.com support for deployment issues
- Telethon GitHub issues for library-specific problems
- n8n community forum for workflow questions

---

*Created by Business Analyst Mary 📊 - Strategic documentation for seamless Telegram-to-n8n integration*
