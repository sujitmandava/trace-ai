# src/trace_ai/agent/orchestrator.py
from __future__ import annotations
from trace_ai.observability.logger import AuditLogger
from pathlib import Path

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import time
import uuid

from trace_ai.checklists.loader import load_checklist
from trace_ai.checklists.evaluator import evaluate_checklist
from trace_ai.agent.decision_policy import decide


class ComplianceOrchestrator:
    """
    Runs the end-to-end compliance workflow:
    - load checklist
    - run checklist evaluation (retrieval + evidence bundling)
    - apply deterministic decision policy
    - return a report object suitable for API/UI + audit logging
    """
    def __init__(
        self,
        retriever,
        *,
        tau_uncertain_rate: float = 0.25,
        audit_log_path: Path = Path("logs/audit.json")
    ):
        self.retriever = retriever
        self.tau_uncertain_rate = tau_uncertain_rate
        self.logger = AuditLogger(audit_log_path)


    def run(
        self,
        *,
        doc_id: str,
        checklist_path: Path,
        run_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        t0 = time.time()
        run_id = str(uuid.uuid4())

        checklist = load_checklist(checklist_path)

        # 1) Evaluate checklist (retrieval-driven, citation-ready)
        results: List[Dict[str, Any]] = evaluate_checklist(checklist, self.retriever, doc_id)

        # 2) Decision gate (deterministic)
        decision_summary = decide(
            checklist,
            results,
            tau_uncertain_rate=self.tau_uncertain_rate
        )

        # 3) Assemble report (what API/UI consumes)
        report = {
            "run_id": run_id,
            "doc_id": doc_id,
            "checklist_id": checklist["checklist_id"],
            "checklist_version": checklist.get("version"),
            "decision": decision_summary.decision,
            "confidence": decision_summary.confidence,
            "reasons": decision_summary.reasons,
            "stats": decision_summary.stats,
            "results": results,
            "timing": {
                "latency_ms": int((time.time() - t0) * 1000)
            },
            "run_metadata": run_metadata or {},
        }

        self.logger.log(report)
        
        return report
