# src/trace_ai/retrieval/retriever.py

from typing import List, Dict
from trace_ai.embeddings.embedder import embed_texts
from trace_ai.embeddings.vector_store import VectorStore


class EvidenceRetriever:
    def __init__(
        self,
        doc_store: VectorStore,
        policy_store: VectorStore,
        top_k: int = 5
    ):
        self.doc_store = doc_store
        self.policy_store = policy_store
        self.top_k = top_k

    def retrieve(
        self,
        doc_query: str,
        policy_query: str | None = None
    ) -> Dict[str, List[Dict]]:

        query_embedding = embed_texts([doc_query])[0]

        doc_results = self.doc_store.search(
            query_embedding=query_embedding,
            k=self.top_k
        )

        policy_results = []
        if policy_query:
            policy_embedding = embed_texts([policy_query])[0]
            policy_results = self.policy_store.search(
                query_embedding=policy_embedding,
                k=self.top_k
            )

        return {
            "document_evidence": doc_results,
            "policy_evidence": policy_results
        }
