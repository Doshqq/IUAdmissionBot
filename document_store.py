import pandas as pd
from datetime import datetime
from vector import model, encode
from db import documents, categories


async def save_document(doc_id: str, text: str, category: str, lang: str = "ru"):
    formatted_text = f"passage: {text}"
    embedding = encode(formatted_text).tolist()
    print(len(embedding))

    doc = {
        "id": doc_id,
        "data": text,
        "category": category,
        "lang": lang,
        "embedding": embedding,
        "created_at": datetime.now(),
    }
    await documents.insert_one(doc)


async def search_similar_documents(query_text: str, limit: int = 4):
    user_query = f"query: {query_text}"
    query_embedding = encode(user_query).tolist()
    print(len(query_embedding))

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": limit,
                "similarity": "cosine",
            }
        },
        {
            "$project": {
                "score": {"$meta": "vectorSearchScore"},
                "data": 1
            }
        }
    ]

    cursor = documents.aggregate(pipeline)
    return [doc async for doc in cursor]


async def get_categories() -> list[str]:
    cursor = categories.find({}, {"name": 1})
    return [doc["name"] async for doc in cursor]


async def get_category_stats() -> dict:
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    cursor = documents.aggregate(pipeline)
    stats = {}
    async for doc in cursor:
        stats[doc["_id"]] = doc["count"]
    return stats


async def export_documents_to_excel() -> str:
    cursor = documents.find()
    docs = []
    async for doc in cursor:
        doc["id"] = str(doc.get("id", doc.get("_id", "")))
        doc.pop("_id", None)
        docs.append(doc)

    df = pd.DataFrame(docs)

    filename = f"documents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = f"/tmp/{filename}"
    df.to_excel(filepath, index=False)
    return filepath