# src/trace_ai/evaluation/regression.py

import json
from pathlib import Path
from typing import Dict, List

from trace_ai.agent.orchestrator import ComplianceOrchestrator
from trace_ai.evaluation.metrics import (
    decision_accuracy,
    false_approval,
    missed_critical_items,
)


class RegressionEvaluator:
    def __init__(
        self,
        orchestrator: ComplianceOrchestrator,
        checklist_path: Path,
        labels_path: Path,
    ):
        self.orchestrator = orchestrator
        self.checklist_path = checklist_path
        self.labels_path = labels_path

    def run(self) -> Dict:
        summaries = []
        failures = []

        label_files = list(self.labels_path.glob("*.json"))

        for label_file in label_files:
            label = json.loads(label_file.read_text())
            doc_id = label["doc_id"]

            report = self.orchestrator.run(
                doc_id=doc_id,
                checklist_path=self.checklist_path,
                run_metadata={"regression": True}
            )

            expected_decision = label["expected_decision"]
            expected_missing = label.get("expected_missing_items", [])

            summary = {
                "doc_id": doc_id,
                "expected_decision": expected_decision,
                "actual_decision": report["decision"],
                "decision_correct": decision_accuracy(
                    expected_decision, report["decision"]
                ),
                "false_approval": false_approval(
                    expected_decision, report["decision"]
                ),
                "missed_critical_items": missed_critical_items(
                    expected_missing, report["results"]
                ),
            }

            summaries.append(summary)

            if summary["false_approval"] or summary["missed_critical_items"]:
                failures.append(summary)

        return {
            "total_docs": len(summaries),
            "summaries": summaries,
            "failures": failures,
            "false_approval_rate": sum(
                1 for s in summaries if s["false_approval"]
            ) / max(1, len(summaries)),
        }
