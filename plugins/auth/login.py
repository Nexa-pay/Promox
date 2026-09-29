# plugins/auth/login.py
import os
import json
from pyrogram import Client, filters
from database.mongo import db

# Temporary dictionaries to hold state during the OTP process
temp_clients = {}
auth_data = {}

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")

# --- LOGIN VIA OTP FLOW ---

@Client.on_message(filters.command("login") & filters.private & filters.user("OWNER_ID"))
async def login_number(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/login +1234567890`")
        
    phone = message.command[1]
    msg = await message.reply_text(f"⏳ Requesting OTP for {phone}...")
    
    # Create an in-memory client to request the code
    temp_client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)
    await temp_client.connect()
    
    try:
        code_info = await temp_client.send_code(phone)
        temp_clients[message.chat.id] = temp_client
        auth_data[message.chat.id] = {"phone": phone, "phone_code_hash": code_info.phone_code_hash}
        
        await msg.edit_text("✅ OTP sent! Check your Telegram app.\n\nReply with: `/otp 12345`")
    except Exception as e:
        await temp_client.disconnect()
        await msg.edit_text(f"❌ Failed: `{e}`")

@Client.on_message(filters.command("otp") & filters.private & filters.user("OWNER_ID"))
async def verify_otp(client, message):
    if message.chat.id not in temp_clients:
        return await message.reply_text("❌ No active login process. Use /login first.")
        
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/otp 12345`")
        
    code = message.command[1]
    temp_client = temp_clients[message.chat.id]
    phone = auth_data[message.chat.id]["phone"]
    phone_hash = auth_data[message.chat.id]["phone_code_hash"]
    
    msg = await message.reply_text("⏳ Verifying OTP...")
    
    try:
        await temp_client.sign_in(phone, phone_hash, code)
        session_string = await temp_client.export_session_string()
        me = await temp_client.get_me()
        
        # Save to MongoDB Forever
        await db.assistants.update_one(
            {"user_id": me.id}, 
            {"$set": {"session_string": session_string, "first_name": me.first_name}}, 
            upsert=True
        )
        
        await msg.edit_text(f"✅ **Login Successful!**\n\nAccount `{me.first_name}` saved to MongoDB.\n*Restart the bot to activate this assistant in Voice Chats.*")
        
    except Exception as e:
        await msg.edit_text(f"❌ Failed: `{e}`")
    finally:
        await temp_client.disconnect()
        del temp_clients[message.chat.id]
        del auth_data[message.chat.id]

# --- LOGIN VIA SESSION FILE UPLOAD ---

@Client.on_message(filters.document & filters.private & filters.user("OWNER_ID"))
async def handle_session_file(client, message):
    file_name = message.document.file_name
    
    if file_name.endswith((".json", ".session")):
        msg = await message.reply_text("📥 Extracting session from file...")
        file_path = await message.download()
        
        try:
            with open(file_path, "r") as f:
                data = f.read()
                
            session_string = json.loads(data).get("session_string") if file_name.endswith(".json") else data.strip()

            if not session_string:
                return await msg.edit_text("❌ No valid session string found.")

            # Test connection
            temp_client = Client(":memory:", session_string=session_string, api_id=API_ID, api_hash=API_HASH)
            await temp_client.start()
            me = await temp_client.get_me()
            await temp_client.stop()
            
            # Save to MongoDB
            await db.assistants.update_one(
                {"user_id": me.id}, 
                {"$set": {"session_string": session_string, "first_name": me.first_name}}, 
                upsert=True
            )
            
            await msg.edit_text(f"✅ **Session Valid!**\nAccount `{me.first_name}` saved to MongoDB.\n*Restart the bot to activate.*")
            
        except Exception as e:
            await msg.edit_text(f"❌ **Error testing session:**\n`{e}`")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
