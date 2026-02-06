# Status Roadmap

**Current State**
- Core pipeline works end to end for demo data: ingestion, retrieval, checklist evaluation, and decisioning.
- Deterministic decision policy and audit logging are implemented.
- Regression evaluator exists for labeled datasets.
- API layer, configs, tests, and documentation are largely stubs.

**Known Gaps**
- `evaluate_checklist` contains a syntax error in a debug print statement.
- Policy evidence is retrieved but not used in scoring.
- Reranking is a naive token overlap heuristic.
- Vector similarity uses inner product without explicit normalization.
- API, schemas, and configs are empty.
- Tests and docs are empty.

**Phase 1: Stabilize Core (Short Term)**
1. Fix the syntax error in `src/trace_ai/checklists/evaluator.py`.
2. Remove debug prints or gate them behind a verbose flag.
3. Normalize embeddings or switch to cosine similarity consistently.
4. Integrate policy evidence into evaluation logic.
5. Add a minimal smoke test suite for ingestion, retrieval, and decisioning.

**Phase 2: Service Layer (Mid Term)**
1. Implement API app, routes, and request/response schemas.
2. Add configuration for thresholds, model names, and storage paths.
3. Introduce structured error handling and consistent logging.

**Phase 3: Evaluation and Quality (Mid Term)**
1. Expand regression datasets and labels.
2. Add faithfulness and citation quality metrics.
3. Track false approvals and missed critical items over time.

**Phase 4: Productization (Long Term)**
1. Add policy management and versioning.
2. Add persistent storage for vector stores and audit logs.
3. Introduce role-based access and review workflows.
4. Produce end-user documentation and operational runbooks.
