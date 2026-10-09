import os
import time
import chromadb
from app.ingestion.jira_parser import JiraParser
from app.ingestion.code_scanner import CodeScanner
from app.ingestion.manifest import Manifest
from app.core.embeddings import get_embedding_client

class Indexer:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_DIR", "./data/chroma"))
        self.jira_collection = self.chroma_client.get_or_create_collection(name="jira_tickets")
        self.code_collection = self.chroma_client.get_or_create_collection(name="code_chunks")
        self.manifest = Manifest(os.getenv("CACHE_DIR", "./data/cache"))
        self.embedding_client = get_embedding_client()
        
    def rebuild(self, force: bool = False):
        start_time = time.time()
        
        jira_path = os.getenv("JIRA_DUMP_PATH", "./data/jira/jira_tickets_dump.txt")
        if force or self.manifest.is_changed(jira_path, "jira"):
            print("Ingesting Jira tickets...")
            parser = JiraParser(jira_path)
            tickets = parser.parse()
            chunks = parser.chunk_tickets(tickets)
            
            if chunks:
                texts = [c.text for c in chunks]
                metadatas = [c.metadata for c in chunks]
                ids = [f"jira_{i}" for i in range(len(chunks))]
                embeddings = self.embedding_client.embed_documents(texts)
                
                # Delete existing
                try:
                    self.chroma_client.delete_collection("jira_tickets")
                    self.jira_collection = self.chroma_client.create_collection("jira_tickets")
                except:
                    pass
                    
                self.jira_collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
                self.manifest.update(jira_path, "jira")
                
                from app.retrieval.bm25_store import BM25Store
                jira_bm25 = BM25Store("jira_tickets")
                jira_bm25.build(texts, metadatas)

        code_dir = os.getenv("CODE_DIR", "./sample_app")
        # For simplicity in this hackathon, we'll re-index code if force is true or if it's the first time
        # A full incremental hash check would iterate over all files
        if force or not self.code_collection.count():
            print("Ingesting Code...")
            scanner = CodeScanner(code_dir)
            chunks = scanner.scan_and_chunk()
            
            if chunks:
                texts = [c.text for c in chunks]
                metadatas = [c.metadata for c in chunks]
                ids = [f"code_{i}" for i in range(len(chunks))]
                
                # Simple batching for embeddings
                batch_size = 50
                try:
                    self.chroma_client.delete_collection("code_chunks")
                    self.code_collection = self.chroma_client.create_collection("code_chunks")
                except:
                    pass

                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    batch_embeddings = self.embedding_client.embed_documents(batch_texts)
                    self.code_collection.add(
                        ids=ids[i:i+batch_size], 
                        embeddings=batch_embeddings, 
                        documents=batch_texts, 
                        metadatas=metadatas[i:i+batch_size]
                    )
                
                from app.retrieval.bm25_store import BM25Store
                code_bm25 = BM25Store("code_chunks")
                code_bm25.build(texts, metadatas)

        self.manifest.save()
        return {"duration": time.time() - start_time}
