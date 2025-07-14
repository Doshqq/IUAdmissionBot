import pandas as pd
from datetime import datetime
from vector import model
from db import documents, categories


async def save_document(doc_id: str, text: str, category: str, lang: str = "ru"):
    embedding = model.encode(text).tolist()
    doc = {
        "id": doc_id,
        "data": text,
        "category": category,
        "lang": lang,
        "embedding": embedding,
        "created_at": datetime.utcnow(),
    }
    await documents.insert_one(doc)


async def search_similar_documents(query_text: str, limit: int = 4):
    query_vector = model.encode(query_text).tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": limit,
                "similarity": "cosine",
                # "returnStoredSource": True,
                # "includeScore": True
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