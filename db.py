import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["admission_bot"]
documents = db["documents"]
categories = db["categories"]