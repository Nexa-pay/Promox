# main.py
import asyncio
import os
import uvloop
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from dotenv import load_dotenv

# Import database connection
from database.mongo import db

load_dotenv()
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store running clients globally so other plugins can access them
app = Client("BotClient", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, plugins=dict(root="plugins"))
active_assistants = {}
active_calls = {}

async def main():
    print("Starting Bot UI...")
    await app.start()
    
    print("Fetching Assistant accounts from MongoDB...")
    # Fetch all stored sessions from the 'assistants' collection
    stored_accounts = db.assistants.find({})
    
    async for account in stored_accounts:
        session = account.get("session_string")
        if not session: continue
            
        # Create a unique pyrogram client for this session
        ass_client = Client(
            f"Assistant_{account['_id']}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session
        )
        
        try:
            await ass_client.start()
            me = await ass_client.get_me()
            
            # Attach VC client
            call_client = PyTgCalls(ass_client)
            await call_client.start()
            
            # Store in global dictionaries using their user ID as the key
            active_assistants[me.id] = ass_client
            active_calls[me.id] = call_client
            print(f"✅ Assistant [{me.first_name}] online.")
            
        except Exception as e:
            print(f"❌ Failed to start an assistant: {e}")

    print("✅ System Online. Press CTRL+C to stop.")
    await idle()

if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
