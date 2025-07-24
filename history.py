from datetime import datetime
from db import db


history_collection = db["chats"]

async def save_history(user_id: int, role: str, msg: dict):
    doc = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "msg": msg,
    }
    await history_collection.insert_one(doc)

async def get_user_history(user_id: int, limit: int = 3):
    cursor = history_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def clear_user_history(user_id: int):
    await history_collection.delete_many({"user_id": user_id})