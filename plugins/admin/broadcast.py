from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.mongo import db # Your motor client connection
import asyncio

scheduler = AsyncIOScheduler()

async def broadcast_job(bot_client, message_text):
    # Fetch all chats from MongoDB
    chats = db.chats.find({})
    async for chat in chats:
        try:
            await bot_client.send_message(chat['chat_id'], message_text)
            await asyncio.sleep(0.3) # Prevent FloodWait errors
        except:
            pass

@Client.on_message(filters.command("setbroadcast") & filters.user("OWNER_ID"))
async def set_broadcast(client, message):
    # Example usage: /setbroadcast 60 Hello World
    # Sets a broadcast every 60 minutes
    args = message.text.split(maxsplit=2)
    interval_minutes = int(args[1])
    text = args[2]
    
    scheduler.add_job(
        broadcast_job, 
        'interval', 
        minutes=interval_minutes, 
        args=[client, text]
    )
    scheduler.start()
    await message.reply_text(f"✅ Broadcast scheduled every {interval_minutes} minutes.")
