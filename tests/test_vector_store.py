from app.retrieval import vector_store


class FakeEmbeddingClient:
    def embed_query(self, query):
        return [0.1, 0.2]


class FakeCollection:
    def __init__(self, results=None):
        self.results = results or {
            "documents": [["current document"]],
            "distances": [[0.0]],
            "metadatas": [[{"source_type": "jira"}]],
        }
        self.queried = False

    def query(self, **kwargs):
        self.queried = True
        return self.results


class FakeChromaClient:
    def __init__(self, path):
        self.stale_collection = FakeCollection()
        self.current_collection = FakeCollection()

    def get_or_create_collection(self, name):
        return self.stale_collection

    def get_collection(self, name):
        return self.current_collection


def test_search_uses_current_collection_after_rebuild(monkeypatch):
    monkeypatch.setattr(vector_store.chromadb, "PersistentClient", FakeChromaClient)
    monkeypatch.setattr(vector_store, "get_embedding_client", FakeEmbeddingClient)

    store = vector_store.VectorStore("jira_tickets")
    results = store.search("latest release")

    assert store.chroma_client.stale_collection.queried is False
    assert store.chroma_client.current_collection.queried is True
    assert results == [{
        "score": 1.0,
        "document": "current document",
        "metadata": {"source_type": "jira"},
    }]
