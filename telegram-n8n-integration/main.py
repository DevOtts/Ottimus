#!/usr/bin/env python3
"""
Telegram to n8n Integration - Main Application
Listens to Telegram messages from whitelisted chats and forwards them to n8n webhooks.

This application uses Telethon to connect to Telegram with user credentials,
processes incoming messages from configured chat IDs, and delivers them to
n8n workflows via HTTP POST webhooks.

Updated for Docker deployment with volume-mounted session storage.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
import requests

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")
n8n_webhook = os.getenv("N8N_WEBHOOK_URL")
whitelist_chats = os.getenv("TELEGRAM_WHITELIST_CHATS", "")

# Validate required environment variables
required_vars = {
    "TELEGRAM_API_ID": api_id,
    "TELEGRAM_API_HASH": api_hash,
    "TELEGRAM_PHONE": phone,
    "N8N_WEBHOOK_URL": n8n_webhook
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please check your environment configuration.")
    exit(1)

# Parse whitelist - convert comma-separated string to list of integers
allowed_chat_ids = []
if whitelist_chats:
    try:
        allowed_chat_ids = [int(chat_id.strip()) for chat_id in whitelist_chats.split(",") if chat_id.strip()]
        logger.info(f"Whitelist configured for {len(allowed_chat_ids)} chats: {allowed_chat_ids}")
    except ValueError as e:
        logger.error(f"Invalid whitelist format: {e}")
        logger.error("Whitelist should be comma-separated chat IDs (e.g., '-1001234567890,123456789')")
        exit(1)
else:
    logger.warning("No whitelist configured - ALL messages will be forwarded! Consider setting TELEGRAM_WHITELIST_CHATS for security.")

# Environment-aware session path
if os.path.exists('/app'):
    # Docker environment - use volume-mounted path
    session_dir = "/app/data"
    if not os.path.exists(session_dir):
        os.makedirs(session_dir, exist_ok=True)
        logger.info(f"Created Docker session directory: {session_dir}")
    session_path = '/app/data/session'
    logger.info("Running in Docker environment")
else:
    # VPS/Local environment - use local session file
    session_path = 'session'
    logger.info("Running in VPS/Local environment")

# Initialize Telegram client with environment-appropriate session path
client = TelegramClient(session_path, api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def message_handler(event):
    """
    Handle incoming messages and forward to n8n webhook (only from whitelisted chats)
    
    This function implements the core message processing workflow:
    1. Check if chat is whitelisted (security filter)
    2. Extract message data into standardized format
    3. Send to n8n webhook via HTTP POST
    4. Handle errors gracefully and log results
    """
    try:
        # Whitelist filtering - security check
        if allowed_chat_ids and event.chat_id not in allowed_chat_ids:
            logger.debug(f"Message from non-whitelisted chat {event.chat_id} - discarding")
            return
        
        # Extract message data into TelegramMessage format
        message_data = {
            "message": event.raw_text or "",  # Handle empty messages
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "date": event.date.isoformat(),
            "is_group": event.is_group,
            "is_channel": event.is_channel,
            "message_id": event.id,  # Current message ID
            "reply_to_msg_id": event.reply_to_msg_id if event.reply_to_msg_id else None  # ID of replied message
        }
        
        # Log successful whitelist match
        chat_type = "group" if event.is_group else "channel" if event.is_channel else "DM"
        message_preview = (message_data["message"][:50] + "...") if len(message_data["message"]) > 50 else message_data["message"]
        reply_info = f" (replying to msg {event.reply_to_msg_id})" if event.reply_to_msg_id else ""
        logger.info(f"New message from {chat_type} {event.chat_id}: {message_preview}{reply_info}")
        
        # Send to n8n webhook with error handling
        await send_to_webhook(message_data)
            
    except Exception as e:
        logger.error(f"Error processing message from chat {getattr(event, 'chat_id', 'unknown')}: {e}")

async def send_to_webhook(message_data):
    """
    Send message data to n8n webhook endpoint
    
    Implements webhook delivery pattern with:
    - HTTP POST with JSON payload
    - 30-second timeout
    - Status code validation
    - Error logging and graceful failure handling
    """
    try:
        # Use asyncio to run the synchronous requests call in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                n8n_webhook,
                json=message_data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent to n8n: HTTP {response.status_code}")
        else:
            logger.error(f"Webhook error: HTTP {response.status_code} - {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        logger.error("Webhook timeout error - n8n webhook took longer than 30 seconds to respond")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Webhook connection error - failed to connect to n8n webhook: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook request error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending to webhook: {e}")

async def main():
    """
    Main application entry point
    
    Handles:
    - Client initialization and authentication
    - Connection establishment with Telegram API
    - Continuous message listening
    - Graceful shutdown handling
    """
    try:
        logger.info("Starting Telegram to n8n Integration...")
        logger.info(f"Session storage: {session_path}.session")
        logger.info(f"Connecting to Telegram API with phone: {phone}")
        
        # Start the client - this will use existing session or prompt for authentication
        await client.start(phone=lambda: phone)
        
        logger.info("Successfully connected to Telegram!")
        logger.info(f"Webhook endpoint: {n8n_webhook}")
        
        if allowed_chat_ids:
            logger.info(f"Monitoring {len(allowed_chat_ids)} whitelisted chats: {allowed_chat_ids}")
        else:
            logger.warning("No whitelist configured - monitoring ALL chats!")
        
        logger.info("Listening for messages... (Press Ctrl+C to stop)")
        
        # Keep the client running and process messages
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    except Exception as e:
        logger.error(f"Fatal error in main application: {e}")
        raise
    finally:
        logger.info("Shutting down Telegram client...")
        await client.disconnect()
        logger.info("Application stopped.")

if __name__ == "__main__":
    """
    Application entry point
    Run the async main function with proper error handling
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        exit(1)