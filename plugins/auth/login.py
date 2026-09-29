import json
import os
from pyrogram import Client, filters

@Client.on_message(filters.document & filters.private)
async def handle_session_file(client, message):
    file_name = message.document.file_name
    
    if file_name.endswith((".json", ".session")):
        await message.reply_text("📥 Processing session file...")
        file_path = await message.download()
        
        try:
            with open(file_path, "r") as f:
                data = f.read()
                
            # If it's a JSON file, extract the session string
            if file_name.endswith(".json"):
                json_data = json.loads(data)
                session_string = json_data.get("session_string")
            else:
                # If it's a raw .session file
                session_string = data.strip()
                
            if not session_string:
                return await message.reply_text("❌ No valid session string found in the file.")

            # Test the session string by starting a temporary client
            temp_client = Client(":memory:", session_string=session_string, api_id=os.getenv("API_ID"), api_hash=os.getenv("API_HASH"))
            await temp_client.start()
            me = await temp_client.get_me()
            await temp_client.stop()
            
            await message.reply_text(f"✅ **Session Valid!**\nSuccessfully logged in as: {me.first_name}")
            # Here: Save this session_string to MongoDB tied to the user's account
            
        except Exception as e:
            await message.reply_text(f"❌ **Invalid Session File:**\n`{e}`")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
