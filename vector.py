from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")
model = AutoModel.from_pretrained("intfloat/multilingual-e5-large")

def encode(texts):
    print("Encoding:", texts)
    if isinstance(texts, str):
        texts = [texts]
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    print("Tokenized inputs:", inputs)
    with torch.no_grad():
        outputs = model(**inputs)
        print("Model outputs ready")
        embeddings = outputs.last_hidden_state.mean(dim=1)  # mean pooling
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    return embeddings[0]

# text = "passage: В Иннополисе можно обучаться по направлениям ИИ и компьютерные науки."
# query = "query: Где можно учиться искусственному интеллекту?"
#
# vec1 = encode(text)
# vec2 = encode(query)
#
# print(1 - cosine(vec1, vec2))  # Должно быть 0.6–0.9+

# async def encode(text):
#     t = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
#     with torch.no_grad():
#         model_output = model(**{k: v.to(model.device) for k, v in t.items()})
#     embeddings = model_output.last_hidden_state[:, 0, :]
#     embeddings = torch.nn.functional.normalize(embeddings)
#     return embeddings[0].cpu()