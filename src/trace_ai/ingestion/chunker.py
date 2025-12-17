# src/trace_ai/ingestion/chunker.py

from typing import List, Dict
import uuid

def chunk_text(
    document: Dict,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[Dict]:

    text = document["text"]
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "doc_id": document["doc_id"],
            "text": chunk_text,
            "start_word": i,
            "end_word": i + len(chunk_words)
        })

        i += chunk_size - overlap

    return chunks
