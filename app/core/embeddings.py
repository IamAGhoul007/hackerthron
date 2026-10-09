import os
from abc import ABC, abstractmethod
from typing import List
from sentence_transformers import SentenceTransformer

class EmbeddingClient(ABC):
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

class LocalEmbeddingClient(EmbeddingClient):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Zero API keys required
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

class DummyGeminiEmbeddingClient(EmbeddingClient):
    def embed_query(self, text: str) -> List[float]:
        return [0.0] * 384
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * 384 for _ in texts]

class DummyOpenAIEmbeddingClient(EmbeddingClient):
    def embed_query(self, text: str) -> List[float]:
        return [0.0] * 1536
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * 1536 for _ in texts]

def get_embedding_client() -> EmbeddingClient:
    provider = os.getenv("EMBEDDING_PROVIDER", "local")
    if provider == "openai":
        return DummyOpenAIEmbeddingClient()
    elif provider == "gemini":
        return DummyGeminiEmbeddingClient()
    else:
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        return LocalEmbeddingClient(model_name)
