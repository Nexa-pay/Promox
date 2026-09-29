import string
import random
from pyrogram import Client, filters
from database.mongo import redeemdb, usersdb

# Generate random 10-character code
def generate_code(length=10):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

@Client.on_message(filters.command("gen") & filters.user("OWNER_ID"))
async def generate_redeem_code(client, message):
    code = generate_code()
    # Insert code into database with an 'unused' status
    await redeemdb.insert_one({"code": code, "used": False})
    await message.reply_text(f"🎟 **New Redeem Code Generated:**\n\n`{code}`\n\nUsers can use `/redeem {code}` to claim it.")

@Client.on_message(filters.command("redeem"))
async def redeem_code(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/redeem <code>`")
    
    code = message.command[1]
    code_data = await redeemdb.find_one({"code": code})
    
    if not code_data:
        return await message.reply_text("❌ Invalid code.")
    if code_data["used"]:
        return await message.reply_text("❌ This code has already been used.")
    
    # Mark code as used and upgrade user
    await redeemdb.update_one({"code": code}, {"$set": {"used": True}})
    await usersdb.update_one({"user_id": message.from_user.id}, {"$set": {"is_premium": True}}, upsert=True)
    
    await message.reply_text("✅ **Successfully Redeemed!** You now have premium access.")
