# Trace AI

**Overview**
Trace AI is a prototype compliance copilot for contracts. It ingests documents, retrieves evidence, evaluates a checklist, applies a deterministic decision policy, and logs an auditable report.

**Core Flow**
1. Ingest documents into a vector store.
2. Retrieve evidence per checklist item.
3. Evaluate pass/fail/uncertain with citations.
4. Apply deterministic decisioning.
5. Log a report for audit and review.

**Quickstart**
1. Create `.env.dev` with `OPENAI_API_KEY=...`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Ingest demo docs: `python scripts/ingest_docs.py`.
4. Run a compliance pass: `python scripts/run_compliance_tests.py`.
5. Run regression evaluation: `python scripts/run_evaluation.py`.

**Project Layout**
- `src/trace_ai/ingestion`: load, parse, and chunk documents.
- `src/trace_ai/embeddings`: embeddings and vector store.
- `src/trace_ai/retrieval`: retrieval and reranking.
- `src/trace_ai/checklists`: checklist loading and evaluation.
- `src/trace_ai/agent`: orchestration and decision policy.
- `src/trace_ai/evaluation`: regression metrics and harness.
- `checklists/`: checklist definitions.
- `datasets/`: demo data and labels.
- `scripts/`: runnable entry points.

**Status**
See the status roadmap in `docs/status_roadmap.md`.
