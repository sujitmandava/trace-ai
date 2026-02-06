from trace_ai.embeddings.vector_store import VectorStore


def test_vector_store_search_filters_doc_id():
    store = VectorStore(dim=3)
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]
    metadatas = [
        {"doc_id": "doc-a", "chunk_id": "c1", "text": "alpha"},
        {"doc_id": "doc-b", "chunk_id": "c2", "text": "beta"},
    ]

    store.add(embeddings, metadatas)

    results = store.search([1.0, 0.0, 0.0], k=2, doc_id="doc-a")

    assert len(results) == 1
    assert results[0]["metadata"]["doc_id"] == "doc-a"
