import os
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from collections import defaultdict

from commands.states import ApplicationState
from bot import ADMIN_IDS, dp, router

latest_applications = defaultdict(list)

@dp.message(Command(commands="apply"))
async def start_application(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Колледж", callback_data="apply_college")],
        [InlineKeyboardButton(text="Вуз", callback_data="apply_university")]
    ])
    await message.answer("📨 Отправка документов на:", reply_markup=kb)
    await state.set_state(ApplicationState.choosing_direction)

@dp.callback_query(F.data.startswith("apply_"))
async def apply_choice(callback: CallbackQuery, state: FSMContext):
    direction = callback.data.replace("apply_", "")
    await state.update_data(direction=direction)
    if direction == "college":
        await callback.message.answer("📄 Отправьте 3 фото аттестата (лицевая, учебное заведение, оценки)")
        await state.set_state(ApplicationState.collecting_certificate)
    else:
        await callback.message.answer("📷 Отправьте фото лица анфас (jpeg, jpg, png)")
        await state.set_state(ApplicationState.collecting_photo)

@router.message(ApplicationState.collecting_certificate, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def handle_certificate_upload(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get("certificate", [])
    file = message.photo[-1] if message.photo else message.document

    if message.document:
        ext = os.path.splitext(file.file_name)[-1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            await message.answer("❌ Неверный формат. Разрешены: jpg, jpeg, png")
            return
    files.append(file)
    await state.update_data(certificate=files)

    if len(files) == 3:
        await message.answer("✅ Аттестат загружен. Теперь отправьте фото лица анфас.")
        await state.set_state(ApplicationState.collecting_photo)

@router.message(ApplicationState.collecting_photo, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def handle_photo_upload(message: Message, state: FSMContext):
    file = message.photo[-1] if message.photo else message.document

    if message.document:
        ext = os.path.splitext(file.file_name)[-1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            await message.answer("❌ Неверный формат. Разрешены: jpg, jpeg, png")
            return

    data = await state.get_data()
    direction = data["direction"]
    certificate = data.get("certificate", [])
    photo = file

    latest_applications[direction].insert(0, {"certificate": certificate, "photo": photo})
    latest_applications[direction] = latest_applications[direction][:2]

    await message.answer("✅ Заявка отправлена!")
    for admin_id in ADMIN_IDS:
        await message.bot.send_message(admin_id, f"📬 Новая заявка на {direction.upper()} от {message.from_user.full_name}, @{message.from_user.username}",
                                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                           [InlineKeyboardButton(text="🔙 Check now?", callback_data="view_applications")]
                                       ])
                                       )
    await state.clear()

