from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_reply_markup(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data=f"reply_{user_id}")]
        ]
    )