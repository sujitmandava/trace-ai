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
from trace_ai.evaluation.regression import RegressionEvaluator

DOC_STORE = Path("storage/doc_store")
POLICY_STORE = Path("storage/policy_store")

doc_store = VectorStore.load(DOC_STORE)
policy_store = (
    VectorStore.load(POLICY_STORE)
    if POLICY_STORE.exists()
    else VectorStore(dim=3072)
)

retriever = EvidenceRetriever(doc_store, policy_store)

orchestrator = ComplianceOrchestrator(
    retriever=retriever,
    audit_log_path=Path("logs/audit.jsonl")
)

evaluator = RegressionEvaluator(
    orchestrator=orchestrator,
    checklist_path=Path("checklists/contract_approval_v0.1.yaml"),
    labels_path=Path("datasets/demo_pack_v0.1/labels"),
)

report = evaluator.run()

print("Total docs:", report["total_docs"])
print("False approval rate:", report["false_approval_rate"])

if report["failures"]:
    print("\nFAILURES:")
    for f in report["failures"]:
        print(f)
else:
    print("\nAll checks passed.")
