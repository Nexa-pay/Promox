from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteRequestSent, InviteHashExpired
from pytgcalls.types import AudioPiped 

@Client.on_message(filters.command("joinvc") & filters.user("OWNER_ID"))
async def auto_join_vc(client, message):
    # Import your instances from your main entry point
    from main import assistant, call_py 
    
    status_msg = await message.reply_text("⏳ Processing...")
    
    # 1. Determine target: Link/Username from arguments OR the current chat ID
    if len(message.command) > 1:
        target = message.command[1]  # e.g., https://t.me/+AbcDef123 or @groupname
    else:
        target = message.chat.id     

    # 2. Assistant joins the text group
    chat_id = None
    try:
        await status_msg.edit_text("🔄 Assistant is joining the group...")
        chat = await assistant.join_chat(target)
        chat_id = chat.id
        await status_msg.edit_text("✅ Assistant joined the group!")
        
    except UserAlreadyParticipant:
        # Assistant is already in the group.
        # If target was a link, Pyrogram won't return the Chat object to get the ID.
        if isinstance(target, str) and target.startswith("http"):
            if str(message.chat.id).startswith("-100"):
                chat_id = message.chat.id # Fallback to the chat where command was sent
            else:
                return await status_msg.edit_text("❌ Assistant is already in the group, but I can't extract the ID from the link. Please run `/joinvc` directly inside the target group.")
        else:
            chat_id = target
            
    except InviteRequestSent:
        return await status_msg.edit_text("⚠️ The group requires admin approval to join. Request sent.")
    except InviteHashExpired:
        return await status_msg.edit_text("❌ The invite link has expired or is invalid.")
    except Exception as e:
        return await status_msg.edit_text(f"❌ Failed to join group: `{e}`")

    # 3. Assistant joins the Voice Chat
    try:
        await status_msg.edit_text("🎙 Connecting to Voice Chat...")
        
        # Use .play() for PyTgCalls 3.0+ (use .join_group_call() for older 1.x/2.x versions)
        await call_py.play(
            chat_id,
            AudioPiped("path_to_your_audio.mp3") 
        )
        await status_msg.edit_text("✅ Successfully connected to the Voice Chat!")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ VC Connection Failed: `{e}`\n*(Make sure the VC is already started in the group)*")
