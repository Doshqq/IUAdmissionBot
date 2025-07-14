# from vector import model, collection
#
#
# def process(query):
#     query_vec = model.encode(query)
#     results = collection.query(query_embeddings=[query_vec], n_results=3)
#     retrieved_texts = [r for r in results['documents'][0]]
#     return retrieved_texts[:3]
#
#
# if __name__ == '__main__':
#     query = "Когда я смогу поступить?"
#     retrieved_documents = process(query)
#
#     # Prompt
#     prompt = f"""
#     You — are a helpful university assistant. Answer strictly based on documents.
#     Question: {query}
#     Most suitable documents:
#     {retrieved_documents[0]}
#     {retrieved_documents[1]}
#
#     Answer:
#     """
#
#     print("Retrieved documents:", retrieved_documents)
#
#     print("Prompt:", prompt)
#
