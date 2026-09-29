from pyrogram import Client, filters
from pytgcalls.types import AudioPiped # Or MediaStream for newer versions

@Client.on_message(filters.command("joinvc") & filters.user("OWNER_ID"))
async def join_vc(client, message):
    chat_id = message.chat.id
    try:
        # The bot tells the assistant to join the chat if it isn't in it
        # await assistant.join_chat(chat_id)
        
        # Join the voice chat
        await call_py.join_group_call(
            chat_id,
            AudioPiped("path_to_audio.mp3") # Placeholder stream
        )
        await message.reply_text("✅ Assistant joined the Voice Chat.")
    except Exception as e:
        await message.reply_text(f"❌ Failed: {e}")

@Client.on_message(filters.command("leavevc") & filters.user("OWNER_ID"))
async def leave_vc(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("👋 Assistant left the Voice Chat.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
