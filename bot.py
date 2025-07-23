import os

from aiogram.exceptions import TelegramBadRequest
from dotenv import load_dotenv
from pathlib import Path
from aiogram import F, Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import StateFilter, Command

import document_store
from llm import get_answer
from utils.logger import logger
from history import get_user_history


dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv("TOKEN")

bot = Bot(token=str(TOKEN), default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
router = Router()
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

try:
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS").split(",")]
except ValueError:
    print("ADMIN_IDS is not set in .env file")


@router.message(Command(commands="history"))
async def show_history(ctx: Message):
    history = await get_user_history(ctx.from_user.id)

    if not history:
        await ctx.answer("История пуста.")
        return

    text = "\n\n".join(
        [f"🕒 {item['timestamp']}\n💭 {item['msg']}" for item in history]
    )

    await ctx.answer(text[:4000])

async def err_msg(ctx):
    await ctx.answer(
        "Sorry, I'm having troubles. Please try again later.",
    )

# @router.message(StateFilter(None), F.text)
# async def question_processor(ctx: Message):
#     question = ctx.text
#     retrieved_documents = await document_store.search_similar_documents(question)
#     await bot.send_chat_action(ctx.chat.id, "typing", request_timeout=5)
#     response = await get_answer(ctx, question, retrieved_documents)
#
#     if response is None:
#         logger.error(f'No response received')
#         await err_msg(ctx)
#         return
#
#     try:
#         await ctx.answer(response)
#     except TelegramBadRequest as e:
#         print("Got an error with Telegram Parsing: ", e, "\nTrying with parse_mode=None")
#         await ctx.answer(response, parse_mode=None)
