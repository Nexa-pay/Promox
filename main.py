import asyncio
import os
import uvloop
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from dotenv import load_dotenv

load_dotenv()

# Initialize Bot Client
app = Client(
    "BotClient",
    api_id=int(os.getenv("API_ID", 0)), # Cast to int safely
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN"),
    plugins=dict(root="plugins") # This loads your plugins folder
)

# Initialize Assistant Client (using Pyrogram Session string)
assistant = Client(
    "AssistantClient",
    api_id=int(os.getenv("API_ID", 0)),
    api_hash=os.getenv("API_HASH"),
    session_string=os.getenv("SESSION_STRING")
)

# Initialize Voice Chat client
call_py = PyTgCalls(assistant)

async def main():
    print("Starting Bot...")
    await app.start()
    
    print("Starting Assistant...")
    await assistant.start()
    
    print("Starting PyTgCalls...")
    await call_py.start()
    
    print("System Online. Press CTRL+C to stop.")
    await idle()

if __name__ == "__main__":
    # uvloop must be initialized BEFORE the asyncio loop starts
    uvloop.install()
    asyncio.run(main())
