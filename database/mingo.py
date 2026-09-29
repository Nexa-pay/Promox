import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["VC_Manager_Bot"]

# Collections
usersdb = db["users"]
redeemdb = db["redeem_codes"]
chatsdb = db["chats"]

async def add_user(user_id: int):
    if not await usersdb.find_one({"user_id": user_id}):
        await usersdb.insert_one({"user_id": user_id, "is_premium": False})

async def add_chat(chat_id: int):
    if not await chatsdb.find_one({"chat_id": chat_id}):
        await chatsdb.insert_one({"chat_id": chat_id, "spam_protection": True})
