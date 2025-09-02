#!/usr/bin/env python3
"""
Chat ID Discovery Script
Lists all your Telegram chats with their IDs for whitelist configuration.
Updated for Docker deployment with /app/data session storage.
"""

import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

# Load environment variables from .env file
load_dotenv()

# Load environment variables
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")

if not all([api_id, api_hash, phone]):
    print("❌ Missing environment variables. Make sure .env is configured.")
    exit(1)

# Docker-compatible session path - create data directory if it doesn't exist
session_dir = "/app/data"
if not os.path.exists(session_dir):
    os.makedirs(session_dir, exist_ok=True)
    print(f"Created session directory: {session_dir}")

# Initialize client with Docker volume session path
client = TelegramClient('/app/data/session', api_id, api_hash)

async def discover_chats():
    """List all chats with their IDs and types"""
    await client.start(phone=lambda: phone)
    
    print("🔍 Discovering your chats and their IDs:")
    print("=" * 60)
    
    groups = []
    channels = []
    users = []
    
    async for dialog in client.iter_dialogs():
        chat_info = {
            'name': dialog.name,
            'id': dialog.id,
            'type': 'Group' if dialog.is_group else 'Channel' if dialog.is_channel else 'User'
        }
        
        if dialog.is_group:
            groups.append(chat_info)
        elif dialog.is_channel:
            channels.append(chat_info)
        else:
            users.append(chat_info)
    
    # Display results
    if groups:
        print("\n📢 GROUPS:")
        for chat in groups[:10]:  # Limit to first 10
            print(f"  {chat['name'][:40]:<40} | ID: {chat['id']}")
    
    if channels:
        print("\n📺 CHANNELS:")
        for chat in channels[:10]:  # Limit to first 10
            print(f"  {chat['name'][:40]:<40} | ID: {chat['id']}")
    
    if users:
        print(f"\n👤 DIRECT MESSAGES: {len(users)} total (showing first 5)")
        for chat in users[:5]:  # Limit to first 5
            print(f"  {chat['name'][:40]:<40} | ID: {chat['id']}")
    
    print("\n" + "=" * 60)
    print("📋 Example whitelist configuration:")
    
    # Generate example whitelist
    example_ids = []
    if groups:
        example_ids.extend([str(g['id']) for g in groups[:2]])
    if channels:
        example_ids.extend([str(c['id']) for c in channels[:1]])
    if users:
        example_ids.extend([str(u['id']) for u in users[:1]])
    
    if example_ids:
        print(f"TELEGRAM_WHITELIST_CHATS={','.join(example_ids)}")
    else:
        print("No chats found. Make sure you have Telegram groups/chats to monitor.")

if __name__ == "__main__":
    asyncio.run(discover_chats())