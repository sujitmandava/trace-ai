# scripts/ingest_docs.py
from pathlib import Path
import sys

# Allow running the script directly without installing the package
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
env_path = ROOT / ".env.dev"
load_dotenv(dotenv_path=env_path)

from trace_ai.ingestion.loader import load_documents
from trace_ai.ingestion.parser import parse_document
from trace_ai.ingestion.chunker import chunk_text
from trace_ai.embeddings.embedder import embed_texts
from trace_ai.embeddings.vector_store import VectorStore

docs_path = ROOT / "datasets/demo_pack_v0.1/docs"

documents = load_documents(docs_path)
store = VectorStore(dim=3072)

for doc_path in documents:
    doc = parse_document(doc_path)
    chunks = chunk_text(doc)

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    store.add(embeddings, chunks)

print(f"Ingested {len(store.metadata)} chunks.")

store.save(Path("storage/doc_store"))