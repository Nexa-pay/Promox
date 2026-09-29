import os
import asyncio
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.mongo import db # Your motor client connection

scheduler = AsyncIOScheduler()

# Safely load the OWNER_ID from your .env file
OWNER_ID = int(os.getenv("OWNER_ID", 0))

async def broadcast_job(bot_client, message_text):
    # Fetch all chats from MongoDB
    chats = db.chats.find({})
    async for chat in chats:
        try:
            await bot_client.send_message(chat['chat_id'], message_text)
            await asyncio.sleep(0.3) # Prevent FloodWait errors
        except:
            pass

@Client.on_message(filters.command("setbroadcast") & filters.user(OWNER_ID))
async def set_broadcast(client, message):
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        return await message.reply_text("Usage: `/setbroadcast <minutes> <message>`")
        
    try:
        interval_minutes = int(args[1])
    except ValueError:
        return await message.reply_text("❌ Interval must be a number (in minutes).")
        
    text = args[2]
    
    scheduler.add_job(
        broadcast_job, 
        'interval', 
        minutes=interval_minutes, 
        args=[client, text]
    )
    
    if not scheduler.running:
        scheduler.start()
        
    await message.reply_text(f"✅ Broadcast scheduled every {interval_minutes} minutes.")
