import aiohttp
from history import get_user_history, save_history

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1:8b"

async def get_answer(ctx, question, documents):
    system_prompt = (
        "Ты — виртуальный ассистент вуза приёмной комиссии Университет Иннополис. "
        "Отвечай строго по документам. Напишите свое обращение к абитуриенту (приветствие и т. п.) от вашего имени, много не расписывай."
    )

    user_prompt = f"""Вопрос: {question}
    
    Найденные наиболее подходящие документы (по убыванию):
    {",\n".join(document["data"] for document in documents)}
    """

    history = await get_user_history(ctx.from_user.id)
    messages = []

    if not history:
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        await save_history(ctx.from_user.id, "system", {"role": "system", "content": system_prompt})
        await save_history(ctx.from_user.id, "user", {"role": "user", "content": user_prompt})
    else:
        for msg in history:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                messages.append({'role': msg['role'], 'content': msg['content']})
        messages.append({"role": "user", "content": user_prompt})
        await save_history(ctx.from_user.id, "user", {"role": "user", "content": user_prompt})

    print("PROMPT →", user_prompt)

    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False
            }
            async with session.post(OLLAMA_URL, json=payload) as resp:
                data = await resp.json()
                print("Ollama raw response:", data)  # 👉 добавь это для отладки

                if "message" not in data:
                    raise ValueError("Ollama ответ не содержит поля 'message'")
                reply = data["message"]["content"]

                await save_history(
                    ctx.from_user.id,
                    "assistant",
                    {"role": "assistant", "content": reply}
                )
                print("RESPONSE ←", reply)
                return reply

    except Exception as e:
        print("Failed to get response from Ollama:", e)
        return "Произошла ошибка при обработке запроса."