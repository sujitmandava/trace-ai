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

from trace_ai.embeddings.vector_store import VectorStore
from trace_ai.retrieval.retriever import EvidenceRetriever
from trace_ai.agent.orchestrator import ComplianceOrchestrator

# NOTE:
# This assumes you reused the same VectorStore instance from ingestion.
# In production you would persist/load it.

# SOLELY FOR TEST
# from trace_ai.ingestion.loader import load_documents
# from trace_ai.ingestion.parser import parse_document
# from trace_ai.ingestion.chunker import chunk_text
# from trace_ai.embeddings.embedder import embed_texts

# docs_path = ROOT / "datasets/demo_pack_v0.1/docs"

# documents = load_documents(docs_path)
# doc_store = VectorStore(dim=3072)

# for doc_path in documents:
#     doc = parse_document(doc_path)
#     chunks = chunk_text(doc)

#     texts = [c["text"] for c in chunks]
#     embeddings = embed_texts(texts)

#     doc_store.add(embeddings, chunks)

# print(f"Ingested {len(doc_store.metadata)} chunks.")

# DEV Code -> Will change to a Docker volume mounted storage 
doc_store = VectorStore.load(ROOT /"storage/doc_store")
policy_store = VectorStore.load(ROOT /"storage/policy_store") \
    if (ROOT / "storage/policy_store").exists() else VectorStore(dim=3072)

retriever = EvidenceRetriever(doc_store, policy_store)

orchestrator = ComplianceOrchestrator(
    retriever=retriever,
    audit_log_path=Path("logs/audit.json")
)

report = orchestrator.run(
    doc_id="missing_law",
    checklist_path=Path("checklists/contract_approval_v0.1.yaml")
)

print(report["decision"])
print(report["confidence"])
for r in report["results"]:
    print(r["item_id"], r["status"])
