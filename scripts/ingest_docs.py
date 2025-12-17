# scripts/ingest_docs.py

from pathlib import Path
from trace_ai.ingestion.loader import load_documents
from trace_ai.ingestion.parser import parse_document
from trace_ai.ingestion.chunker import chunk_text
from trace_ai.embeddings.embedder import embed_texts
from trace_ai.embeddings.vector_store import VectorStore

docs_path = Path("datasets/demo_pack_v0.1/docs")

documents = load_documents(docs_path)
store = VectorStore(dim=3072)

for doc_path in documents:
    doc = parse_document(doc_path)
    chunks = chunk_text(doc)

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    store.add(embeddings, chunks)

print(f"Ingested {len(store.metadata)} chunks.")
