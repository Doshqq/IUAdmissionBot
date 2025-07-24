from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import bold

from apply_parser import search
from bot import dp
from utils.program_data import get_mapped_abiturient_data, level_map, basis_map, category_map
from utils.states import FindMeState


@dp.message(Command(commands="findme"))
async def start_findme(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="Бакалавриат", callback_data="edu_bachelor")
    builder.button(text="Магистратура", callback_data="edu_master")
    builder.adjust(1)
    await message.answer("Выберите уровень образования:", reply_markup=builder.as_markup())
    await state.set_state(FindMeState.education_level)

@dp.callback_query(F.data.startswith("edu_"))
async def choose_education_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    await state.update_data(education_level=level)

    if level == "bachelor":
        builder = InlineKeyboardBuilder()
        builder.button(text="Бюджетная основа", callback_data="basis_budget")
        builder.button(text="Полное возмещение затрат", callback_data="basis_paid")
        builder.button(text="Целевой приём", callback_data="basis_target")
        builder.button(text="Отмена", callback_data="lists_close")
        builder.adjust(1)
        await callback.message.edit_text("Выберите основу поступления:", reply_markup=builder.as_markup())
        await state.set_state(FindMeState.enrollment_basis)
    else:
        await callback.message.edit_text("Магистратура пока не поддерживается. Мы уже работаем над расширением функционала.")
        await state.clear()

@dp.callback_query(F.data == "lists_close")
async def close_panel(callback: CallbackQuery):
    await callback.message.delete()

@dp.callback_query(F.data.startswith("basis_"))
async def choose_enrollment_basis(callback: CallbackQuery, state: FSMContext):
    basis = callback.data.split("_")[1]
    await state.update_data(enrollment_basis=basis)

    builder = InlineKeyboardBuilder()
    builder.button(text="На общих основаниях", callback_data="cat_general")
    if basis == "budget":
        builder.button(text="Имеющие особое право", callback_data="cat_special")
    builder.adjust(1)
    await callback.message.edit_text("Выберите категорию поступления:", reply_markup=builder.as_markup())
    await state.set_state(FindMeState.enrollment_category)

@dp.callback_query(F.data.startswith("cat_"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(enrollment_category=category)

    data = await state.get_data()
    basis = data["enrollment_basis"]

    programs = [
        "Инженерия информационных систем",
        "Анализ данных и ИИ",
        "Мат. основы ИИ"
    ]
    if basis != "budget":
        programs += [
            "AI360: Инженерия данных",
            "Робототехника"
        ]

    builder = InlineKeyboardBuilder()
    for i, prog in enumerate(programs):
        builder.button(text=prog, callback_data=f"prog_{i}")
    builder.adjust(1)

    await callback.message.edit_text("Выберите программу обучения:", reply_markup=builder.as_markup())
    await state.set_state(FindMeState.program)


@dp.callback_query(F.data.startswith("prog_"))
async def choose_program(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])

    data = await state.get_data()
    basis = data["enrollment_basis"]
    programs = [
        "ИИС",
        "АДиИИ",
        "МОИИ"
    ]
    if basis != "budget":
        programs += [
            "AI360",
            "Робокеки"
        ]

    chosen_program = programs[index]
    await state.update_data(program=chosen_program)

    final_data = await state.get_data()
    response = (
        f"Ваш выбор:\n"
        f"{bold('Уровень образования')}: {level_map.get(final_data['education_level'], '—')}\n"
        f"{bold('Основа')}: {basis_map.get(final_data['enrollment_basis'], '—')}\n"
        f"{bold('Категория')}: {category_map.get(final_data['enrollment_category'], '—')}\n"
        f"{bold('Программа')}: {final_data['program']}"
    )
    await callback.message.edit_text(response)
    await callback.message.answer("✏️ Ваш ID (с госуслуг):")
    await state.set_state(FindMeState.searching)


def format_row_wide(label: str, row: list[str]) -> str:
    if not row:
        return f"*{label}*: _нет данных_"

    return (
        f"*{label}* {row[0]} *месте*\n| "
        f"ID: `{row[1]}` | "
        f"БВИ: {"✅" if len(row[5]) > 1 else "нет"} | "
        f"Баллы за ИД: {row[11]} | "
        f"Сумма баллов(с ИД): {row[12]} |\n| "
        f"Приоритет: {row[3]} | "
        f"Согласие: {"✅" if len(row[2]) > 1 else "нет"}"
    )


def format_search_result_md(target_row: list[str], row_above: list[str] | None = None,
                            row_below: list[str] | None = None) -> str:
    parts = []

    if target_row:
        parts.append(format_row_wide("Вы на", target_row))
    else:
        return "*😕 Вы не найдены в списках.*"

    if row_above:
        parts.append(format_row_wide("⬆️ Выше на", row_above))
    else:
        parts.append("*⬆️ Выше:* _нет_")

    if row_below:
        parts.append(format_row_wide("⬇️ Ниже на", row_below))
    else:
        parts.append("*⬇️ Ниже:* _нет_")

    return "\n\n".join(parts)


@dp.message(FindMeState.searching)
async def start_searching(message: Message, state: FSMContext):
    user_id_from_message = message.text.strip()
    await state.update_data(user_id=user_id_from_message)

    final_data = await state.get_data()

    searching_msg = await message.answer("🔍 Ищу вас в конкурсных списках...")

    response = search(get_mapped_abiturient_data(final_data), user_id_from_message)

    row_above, target_row, row_below = None, None, None
    if response:
        row_above, target_row, row_below = response

    text = format_search_result_md(target_row, row_above, row_below)
    await message.answer(text, parse_mode="Markdown")

    await searching_msg.delete()
    await state.clear()