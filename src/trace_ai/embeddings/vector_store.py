# src/trace_ai/embeddings/vector_store.py

import faiss
import numpy as np
import json
from pathlib import Path
from typing import List, Dict


class VectorStore:
    def __init__(self, dim: int):        
        self.index = faiss.IndexFlatIP(dim)
        self.metadata: List[Dict] = []

    def add(self, embeddings: List[List[float]], metadatas: List[Dict]):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadatas)

    def search(self, query_embedding: List[float], *, k: int = 5, doc_id: str | None = None, oversample: int = 5):
        # print(f"store search; doc_id = {doc_id};")
        q = np.array([query_embedding]).astype("float32")
        # retrieve more than needed to allow filtering
        distances, indices = self.index.search(q, k)

        results = []
        for idx, score in zip(indices[0], distances[0]):
            meta = self.metadata[idx]

            if doc_id is not None and meta.get("doc_id") != doc_id:
                continue

            results.append({
                "metadata": meta,
                "score": float(score)
            })

            if len(results) >= k:
                break

        return results

    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path / "index.faiss"))
        with open(path / "metadata.json", "w") as f:
            json.dump(self.metadata, f)

    @classmethod
    def load(cls, path: Path):
        index = faiss.read_index(str(path / "index.faiss"))
        with open(path / "metadata.json") as f:
            metadata = json.load(f)

        store = cls(index.d)
        store.index = index
        store.metadata = metadata
        return store
