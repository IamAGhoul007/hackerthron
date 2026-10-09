import os
import json
from typing import List, Dict
from rank_bm25 import BM25Okapi

class BM25Store:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.cache_dir = os.getenv("CACHE_DIR", "./data/cache")
        self.bm25 = None
        self.documents = []
        self.metadatas = []
        self._load()

    def _load(self):
        path = os.path.join(self.cache_dir, f"{self.collection_name}_bm25.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.documents = data["documents"]
                self.metadatas = data["metadatas"]
                tokenized_corpus = [doc.split(" ") for doc in self.documents]
                if tokenized_corpus:
                    self.bm25 = BM25Okapi(tokenized_corpus)

    def build(self, documents: List[str], metadatas: List[Dict]):
        self.documents = documents
        self.metadatas = metadatas
        tokenized_corpus = [doc.split(" ") for doc in self.documents]
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)
            
        os.makedirs(self.cache_dir, exist_ok=True)
        path = os.path.join(self.cache_dir, f"{self.collection_name}_bm25.json")
        with open(path, "w") as f:
            json.dump({"documents": self.documents, "metadatas": self.metadatas}, f)

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        if not self.bm25:
            return []
        tokenized_query = query.split(" ")
        scores = self.bm25.get_scores(tokenized_query)
        
        results = []
        for i, score in enumerate(scores):
            results.append({"score": float(score), "document": self.documents[i], "metadata": self.metadatas[i]})
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
