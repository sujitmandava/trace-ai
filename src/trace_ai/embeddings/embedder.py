# src/trace_ai/embeddings/embedder.py

from typing import List
from openai import OpenAI

client = OpenAI()

def embed_texts(texts: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=texts
    )
    return [d.embedding for d in response.data]
