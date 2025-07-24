from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from security import OPERATOR_IDS
from db import db
from utils.messages import get_reply_markup
from utils.states import SupportState


support_router = Router()

@support_router.message(Command("support"))
async def support_command(message: Message, state: FSMContext):
    await message.answer("📬️ Напишите вопрос, который хотите отправить *приёмной комиссии Innopolis University*:")
    await state.set_state(SupportState.waiting_for_question)

@support_router.message(SupportState.waiting_for_question)
async def handle_user_support(message: Message, state: FSMContext):
    for op_id in OPERATOR_IDS:
        await db.bindings.update_one(
            {"operator_id": op_id},
            {"$set": {"user_id": message.from_user.id}},
            upsert=True
        )

        info = (
            f"📩 *Новое сообщение от пользователя:*\n"
            f"*Имя:* {message.from_user.full_name}\n"
            f"*Username:* @{message.from_user.username or '—'}\n"
            f"*ID:* `{message.from_user.id}`"
        )

        if message.text:
            await message.bot.send_message(
                chat_id=op_id,
                text=info + f"\n\n{message.text}",
                reply_markup=get_reply_markup(message.from_user.id),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.send_copy(chat_id=op_id, reply_markup=get_reply_markup(message.from_user.id))

    await message.answer("✅ Ваше сообщение отправлено. Ожидайте ответа.")
    await state.clear()


@support_router.callback_query(F.data.startswith("reply_"))
async def operator_reply_click(callback: CallbackQuery, state: FSMContext):
    _, user_id = callback.data.split("_")
    user_id = int(user_id)

    await state.set_state(SupportState.waiting_for_reply)
    await state.update_data(user_id=user_id)

    await callback.message.answer(f"📮 Напишите ответ для абитуриента `{user_id}`:", parse_mode=ParseMode.MARKDOWN)
    await callback.answer()


@support_router.message(SupportState.waiting_for_reply)
async def handle_operator_reply(message: Message, state: FSMContext):
    if message.from_user.id not in OPERATOR_IDS:
        return

    data = await state.get_data()
    user_id = data.get("user_id")
    if not user_id:
        await message.answer("❌ Неизвестно, кому отвечать. Нажмите 'Ответить' под сообщением пользователя.")
        return

    try:
        caption = f"💬 *Ответ приёмной комиссии Innopolis University:*\n"

        if message.text:
            await message.bot.send_message(chat_id=user_id, text=caption + message.text, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.send_copy(chat_id=user_id, parse_mode=ParseMode.MARKDOWN)

        await message.answer("✅ Ответ отправлен абитуриенту.")
    except Exception as e:
        await message.answer(f"❌ Не удалось отправить сообщение: {e}")

    await state.clear()