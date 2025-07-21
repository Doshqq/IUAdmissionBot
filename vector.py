from sentence_transformers import SentenceTransformer

model = SentenceTransformer('intfloat/multilingual-e5-large')

# Add documents
# docs = [
#     {"id": "doc1", "text": "Поступление возможно до 1 августа", "lang": "ru"},
#     {"id": "doc2", "text": "Applications are accepted until August 1", "lang": "en"},
#     {"id": "doc3", "text": "Заселение в общежитие происходит в конце августа", "lang": "ru"},
# ]

# for doc in docs:
#     embedding = model.encode(doc["text"])
#     collection.add(documents=[doc["text"]], ids=[doc["id"]], embeddings=[embedding])