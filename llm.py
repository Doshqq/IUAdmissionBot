import g4f
from g4f.client import AsyncClient
from g4f.Provider import Blackbox

from history import get_user_history, save_history


async def get_answer(ctx, question, documents):
    client = AsyncClient()
    if not documents:
        return "Извините, я не могу ответить на этот вопрос, так как не могу найти нужные документы."

    system_prompt = """
    Ты — виртуальный ассистент приёмной комиссии Университета Иннополис.
    В начале диалога напиши свое обращение к абитуриенту (приветствие и т. п.) от имени ассистента.
    Отвечай строго и кратко на основании предоставленных ниже документов. Не пересказывай всё подряд — отвечай именно на вопрос пользователя. 
    
    Если ответа в документах нет — скажи об этом прямо, не выдумывай.
    
    **Формат ответа**:
    - Используй только факты из документов.
    - Не используй markdown, заголовки или эмодзи.
    - Пиши на русском языке, официально и понятно.
    
    История сообщений дана только для контекста. Последний вопрос пользователя — самый важный.
    Пользователь задал вопрос:
    """

    user_prompt = f"""
    Пользователь задал вопрос:
    "{question.strip()}"
    
    Ответь кратко и чётко на основании следующих документов:
    
    {'\n\n'.join(f"{i+1}. {doc['data'].strip()}" for i, doc in enumerate(documents))}
    
    Не используй информацию вне этих документов. Не повторяй всё подряд, а выбери только то, что реально помогает ответить на вопрос.
    """
    system_default = {"role": "system", "content": system_prompt}
    user_default = {"role": "user", "content": user_prompt}
    user_question_default = {"role": "user", "content": question.strip()}

    messages = []
    history = await get_user_history(ctx.from_user.id)
    if not history:
        messages.append(system_default)
        messages.append(user_default)
        await save_history(ctx.from_user.id, "system", system_default)
        await save_history(ctx.from_user.id, "user", user_question_default)
    else:
        messages.extend(msg["msg"] for msg in history)
        messages.append(user_default)
        await save_history(ctx.from_user.id, "user", user_question_default)

    print("Messages: ", messages)

    response = None
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini", # gpt-4o-mini
            provider=Blackbox,
            messages=messages,
            web_search=False
        )
    except Exception as e:
        print("Failed to create completion:", e)
    finally:
        print("Response:", response)

    if response:
        await save_history(
            ctx.from_user.id,
            "assistant",
            {"role": "assistant", "content": response.choices[0].message.content}
        )

        return response.choices[0].message.content
    else:
        return None

