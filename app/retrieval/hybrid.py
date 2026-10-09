import os
from typing import List, Dict
from app.retrieval.bm25_store import BM25Store
from app.retrieval.vector_store import VectorStore

class HybridRetriever:
    def __init__(self, collection_name: str):
        self.bm25_store = BM25Store(collection_name)
        self.vector_store = VectorStore(collection_name)
        self.rrf_k = int(os.getenv("RRF_K", "60"))

    def search(self, queries: List[str], top_k: int = 10) -> List[Dict]:
        all_results = {}
        
        for q in queries:
            bm25_res = self.bm25_store.search(q, top_k=top_k*2)
            vector_res = self.vector_store.search(q, top_k=top_k*2)
            
            # Combine and RRF
            for rank, item in enumerate(bm25_res):
                doc = item['document']
                if doc not in all_results:
                    all_results[doc] = {"score": 0.0, "document": doc, "metadata": item['metadata']}
                all_results[doc]["score"] += 1.0 / (self.rrf_k + rank + 1)
                
            for rank, item in enumerate(vector_res):
                doc = item['document']
                if doc not in all_results:
                    all_results[doc] = {"score": 0.0, "document": doc, "metadata": item['metadata']}
                all_results[doc]["score"] += 1.0 / (self.rrf_k + rank + 1)
                
        # Sort by RRF score
        sorted_results = sorted(list(all_results.values()), key=lambda x: x["score"], reverse=True)
        return sorted_results[:top_k]
