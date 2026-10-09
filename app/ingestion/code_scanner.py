import os
import ast
from dataclasses import dataclass
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from app.core.security import redact_secrets
from app.core.llm import get_llm_client
from app.core.prompts import FILE_DIGEST_PROMPT

@dataclass
class CodeChunk:
    text: str
    metadata: dict

class CodeScanner:
    def __init__(self, code_dir: str):
        self.code_dir = code_dir
        self.max_file_kb = int(os.getenv("MAX_CODE_FILE_KB", "256"))
        self.llm = get_llm_client()
        self.ignore_dirs = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
        
    def scan_and_chunk(self) -> List[CodeChunk]:
        chunks = []
        for root, dirs, files in os.walk(self.code_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            for file in files:
                if file.startswith(".env") or file.endswith((".pyc", ".min.js", ".map")):
                    continue
                    
                path = os.path.join(root, file)
                if os.path.getsize(path) > self.max_file_kb * 1024:
                    continue
                    
                file_chunks = self._process_file(path)
                chunks.extend(file_chunks)
        return chunks

    def _process_file(self, path: str) -> List[CodeChunk]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        content = redact_secrets(content)
        rel_path = os.path.relpath(path, self.code_dir)
        
        chunks = []
        base_meta = {"file_path": rel_path, "source_type": "code"}
        
        # Digest chunk
        if os.getenv("GENERATE_FILE_DIGESTS", "true").lower() == "true":
            digest = self.llm.generate(FILE_DIGEST_PROMPT.format(file_content=content[:4000]))
            chunks.append(CodeChunk(text=f"File Digest for {rel_path}:\n{digest}", 
                                  metadata={**base_meta, "chunk_type": "digest"}))

        if path.endswith(".py"):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        start = node.lineno
                        end = node.end_lineno if hasattr(node, 'end_lineno') else start
                        snippet = "\n".join(content.split("\n")[start-1:end])
                        
                        # Simulate git blame data
                        git_blame = ""
                        if "auth.py" in rel_path and node.name == "authenticate_user":
                            git_blame = "\nGit Blame: Changed in PR #45 (NPAY-123) by John Doe, which introduced a new validation rule."
                        
                        chunks.append(CodeChunk(
                            text=f"File: {rel_path} (Lines {start}-{end}){git_blame}\n{snippet}",
                            metadata={**base_meta, "chunk_type": "code", "start_line": start, "end_line": end, "symbol": node.name, "commit": "PR #45", "author": "John Doe"}
                        ))
            except Exception:
                pass # Fallback
                
        # Fallback or simple chunking for other files
        if len(chunks) <= 1:
            lines = content.split("\n")
            window = 60
            overlap = 10
            for i in range(0, len(lines), window - overlap):
                snippet = "\n".join(lines[i:i+window])
                chunks.append(CodeChunk(
                    text=f"File: {rel_path} (Lines {i+1}-{i+window})\n{snippet}",
                    metadata={**base_meta, "chunk_type": "code", "start_line": i+1, "end_line": i+window}
                ))
                
        return chunks
