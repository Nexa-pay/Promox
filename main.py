import asyncio
import uvloop
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Bot Client
app = Client(
    "BotClient",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN"),
    plugins=dict(root="plugins")
)

# Initialize Assistant Client (using Pyrogram Session string)
assistant = Client(
    "AssistantClient",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    session_string=os.getenv("SESSION_STRING")
)

# Initialize Voice Chat client
call_py = PyTgCalls(assistant)

async def main():
    # Set high-performance event loop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    print("Starting Bot...")
    await app.start()
    
    print("Starting Assistant...")
    await assistant.start()
    
    print("Starting PyTgCalls...")
    await call_py.start()
    
    print("System Online. Press CTRL+C to stop.")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
