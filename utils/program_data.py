level_map = {
    "bachelor": "Бакалавриат",
    "master": "Магистратура"
}
basis_map = {
    "budget": "Бюджетная основа",
    "paid": "Полное возмещение затрат",
    "target": "Целевой приём"
}
category_map = {
    "general": "На общих основаниях",
    "special": "Имеющие особое право"
}

programs = {
    "ИИС": "Инженерия информационных систем (09.03.01 Информатика и вычислительная техника)",
    "АДиИИ": "Анализ данных и искусственный интеллект (09.03.01 Информатика и вычислительная техника)",
    "МОИИ": "Математические основы искусственного интеллекта (09.03.01 Информатика и вычислительная техника)",
    "AI360: Инженерия данных": "AI360: Инженерия данных (09.03.01 Информатика и вычислительная техника)",
    "Робокеки": "Робототехника (15.03.06 Мехатроника и робототехника)"
}

def get_mapped_abiturient_data(final_data: dict) -> dict:
    return {
        "education_level": level_map.get(final_data.get("education_level"), "—"),
        "enrollment_basis": basis_map.get(final_data.get("enrollment_basis"), "—"),
        "enrollment_category": category_map.get(final_data.get("enrollment_category"), "—"),
        "program": programs.get(final_data.get("program"), "—"),
    }