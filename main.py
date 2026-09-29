import asyncio
import os
import uvloop
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Safely fetch API credentials
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING")

# 1. Initialize Bot Client (handles buttons, UI, admin commands)
app = Client(
    "BotClient",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins") # Automatically loads all files in the plugins folder
)

# 2. Initialize Assistant Client (Userbot via String Session for VC & Group Joining)
assistant = Client(
    "AssistantClient",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# 3. Initialize Voice Chat client (Attached to the Assistant account)
call_py = PyTgCalls(assistant)

async def main():
    print("Starting Bot...")
    await app.start()
    
    print("Starting Assistant...")
    await assistant.start()
    
    # FIX for "Peer id invalid" errors: 
    # This forces Pyrogram to read all chats the assistant is in and memorize their Access Hashes.
    print("Caching chats to prevent Peer ID errors (this may take a few seconds)...")
    try:
        async for _ in assistant.get_dialogs():
            pass
    except Exception as e:
        print(f"Dialog sync warning: {e}")
    
    print("Starting PyTgCalls...")
    await call_py.start()
    
    print("✅ System Online. Press CTRL+C to stop.")
    await idle()

if __name__ == "__main__":
    # uvloop must be initialized BEFORE the asyncio loop starts for Python 3.12+
    uvloop.install()
    
    # Run the main async loop
    asyncio.run(main())
