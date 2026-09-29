from pyrogram import Client, filters
from database.mongo import chatsdb

# A simple list of blacklisted domains or keywords
BANNED_LINKS = ["t.me/crypto", "freebitcoin", "airdrop"]

@Client.on_message(filters.group & ~filters.me)
async def spam_checker(client, message):
    if not message.text and not message.caption:
        return
        
    chat_data = await chatsdb.find_one({"chat_id": message.chat.id})
    if chat_data and not chat_data.get("spam_protection", True):
        return # Skip if spam protection is disabled for this chat

    text = (message.text or message.caption).lower()
    
    # Check for banned links
    if any(banned in text for banned in BANNED_LINKS):
        try:
            await message.delete()
            await client.restrict_chat_member(
                message.chat.id, 
                message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await message.reply_text(f"🛡 **Spam Detected!** {message.from_user.mention} has been muted.")
        except:
            pass # Bot lacks admin rights
