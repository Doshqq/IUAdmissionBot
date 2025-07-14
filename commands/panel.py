import asyncio
import time
from collections import defaultdict

from aiogram import F, md
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot import dp, router, ADMIN_ID
from utils.files import extract_text
from commands.states import AddingState, CategoryState
from db import db
from document_store import get_categories, get_category_stats, save_document


@dp.message(Command(commands="panel"))
async def show_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("403 Forbidden")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Docs", callback_data="panel_docs")],
        [InlineKeyboardButton(text="❌ Close", callback_data="panel_close")],
        ]
    )
    await message.answer("🔧 Supervising panel:", reply_markup=kb)
    return None

@dp.callback_query(lambda c: c.data == "panel")
async def back_to_panel(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Docs", callback_data="panel_docs")],
            [InlineKeyboardButton(text="❌ Close", callback_data="panel_close")]
        ]
    )
    await callback.message.edit_text("🔧 Supervising panel:", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "panel_close")
async def close_panel(callback: CallbackQuery):
    await callback.message.delete()


@dp.callback_query(lambda c: c.data == "panel_docs")
async def docs_menu(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Info", callback_data="docs_info")],
        [InlineKeyboardButton(text="📥 Add", callback_data="docs_add")],
        [InlineKeyboardButton(text="📚 Open/Save", callback_data="docs_open")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="panel")],
        ]
    )
    await callback.message.edit_text("📄 Manage documents:", reply_markup=kb)


@dp.callback_query(lambda c: c.data == "docs_info")
async def show_info(callback: CallbackQuery):
    stats = get_category_stats()
    total_docs = sum(stats.values())
    text = "📊 Information about documents:\n\n"
    for category, count in stats.items():
        text += f"• {category}: {count} docs\n"
    text += f"\nTotal: {total_docs} documents"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="panel_docs")]
        ]
    ))


# A
@dp.callback_query(lambda c: c.data == "docs_add")
async def choose_category(callback: CallbackQuery):
    categories = await get_categories()  # из БД
    rows = []
    for i in range(0, len(categories), 2):
        row = [
            InlineKeyboardButton(text=categories[i], callback_data=f"add_cat_{categories[i]}")
        ]
        if i + 1 < len(categories):
            row.append(
                InlineKeyboardButton(text=categories[i + 1], callback_data=f"add_cat_{categories[i + 1]}")
            )
        rows.append(row)

    rows.append([InlineKeyboardButton(text="➕ Create new category", callback_data="docs_add_category")])
    rows.append([InlineKeyboardButton(text="🔙 Back", callback_data="panel_docs")])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await callback.message.edit_text("Choose category:", reply_markup=kb)

@router.callback_query(F.data == "docs_add_category")
async def ask_category_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✏️ Write category name:",
    )
    await state.set_state(CategoryState.awaiting_name)


@router.message(CategoryState.awaiting_name)
async def save_category_name(message: Message, state: FSMContext):
    name = message.text.strip()
    exists = db.categories.find_one({"name": name})
    if exists:
        await message.answer(f"⚠️ Category '{name}' already exists. ")
    else:
        db.categories.insert_one({"name": name})
        await message.answer(f"✅ Category '{name}' added.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="panel_docs")]
    ])
    await message.answer("📄 Back to docs menu:", reply_markup=kb)
    await state.clear()


# B
@dp.callback_query(lambda c: c.data.startswith("add_cat_"))
async def ask_document(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("add_cat_", "")
    await state.update_data(category=category)
    await callback.message.answer(f"📎 Send {md.code(".txt")} or {md.code(".md")} file.")
    await state.set_state(AddingState.awaiting_document)


media_groups_cache = defaultdict(list)
# C
@router.message(
    AddingState.awaiting_document,
    F.media_group_id,
    F.content_type == ContentType.DOCUMENT
)
async def handle_media_group_doc(message: Message, state: FSMContext):
    media_groups_cache[message.media_group_id].append(message)

    # Подождать чуть-чуть, чтобы вся группа успела дойти
    await asyncio.sleep(1.5)

    # Проверить, что это последний документ в группе (и он ещё не обработан)
    if message == media_groups_cache[message.media_group_id][-1]:
        docs = media_groups_cache.pop(message.media_group_id)
        data = await state.get_data()
        category = data["category"]

        for msg in docs:
            file = msg.document
            file_info = await message.bot.get_file(file.file_id)
            file_path = f"/tmp/{file.file_name}"
            await message.bot.download_file(file_info.file_path, destination=file_path)
            text = extract_text(file_path)

            doc_id = str(int(time.time() * 1000))
            await save_document(doc_id=doc_id, text=text, category=category)

        await message.answer(
            f"✅ {len(docs)} document(s) saved in category '{category}'.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Back", callback_data="panel_docs")]
            ])
        )
        await state.clear()