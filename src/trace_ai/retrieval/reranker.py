# src/trace_ai/retrieval/reranker.py

from typing import List, Dict
import re


def tokenize(text: str) -> set:
    return set(re.findall(r"\w+", text.lower()))


def rerank(
    query: str,
    results: List[Dict],
    top_k: int = 3
) -> List[Dict]:

    query_tokens = tokenize(query)

    scored = []
    for r in results:
        text = r["metadata"]["text"]
        overlap = len(query_tokens & tokenize(text))
        scored.append((overlap, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_k]]
