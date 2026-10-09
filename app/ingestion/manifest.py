import os
import json
import hashlib
from typing import Dict

class Manifest:
    def __init__(self, cache_dir: str):
        self.manifest_path = os.path.join(cache_dir, "manifest.json")
        self.hashes: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        os.makedirs(os.path.dirname(self.manifest_path), exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(self.hashes, f)

    def get_hash(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def is_changed(self, file_path: str, file_key: str) -> bool:
        current_hash = self.get_hash(file_path)
        return current_hash != self.hashes.get(file_key)

    def update(self, file_path: str, file_key: str):
        self.hashes[file_key] = self.get_hash(file_path)
