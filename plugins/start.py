# plugins/start.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Assistant (Number)", callback_data="help_login")],
        [InlineKeyboardButton("📁 Add Assistant (.session)", callback_data="help_file")]
    ])
    
    await message.reply_text(
        f"**Welcome {message.from_user.first_name}!**\n\n"
        "I am your Multi-Account VC Manager.\n"
        "You can add as many assistant accounts as you want to MongoDB.",
        reply_markup=buttons
    )

@Client.on_callback_query(filters.regex("^help_"))
async def help_callbacks(client, callback_query):
    action = callback_query.data.split("_")[1]
    
    if action == "login":
        await callback_query.message.reply_text("To login via number, send:\n`/login +1234567890`")
    elif action == "file":
        await callback_query.message.reply_text("To login via file, simply send the `.session` or `.json` file to me here.")
