# src/trace_ai/embeddings/vector_store.py

import faiss
import numpy as np
from typing import List, Dict

class VectorStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata: List[Dict] = []

    def add(self, embeddings: List[List[float]], metadatas: List[Dict]):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadatas)

    def search(self, query_embedding: List[float], k: int = 5):
        q = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(q, k)

        results = []
        for idx, score in zip(indices[0], distances[0]):
            results.append({
                "metadata": self.metadata[idx],
                "score": float(score)
            })

        return results
