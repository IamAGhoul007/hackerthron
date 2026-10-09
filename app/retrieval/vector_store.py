import os
import chromadb
from typing import List, Dict
from app.core.embeddings import get_embedding_client

class VectorStore:
    def __init__(self, collection_name: str):
        self.chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_DIR", "./data/chroma"))
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        self.embedding_client = get_embedding_client()

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        query_embedding = self.embedding_client.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                # distance to similarity (approx)
                score = 1.0 / (1.0 + results['distances'][0][i])
                formatted_results.append({
                    "score": score,
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                })
        return formatted_results
