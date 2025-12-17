# src/trace_ai/agent/decision_policy.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple


Decision = Literal["RECOMMEND_APPROVE", "ESCALATE", "REFUSE"]


@dataclass(frozen=True)
class DecisionSummary:
    decision: Decision
    confidence: float
    reasons: List[str]
    stats: Dict[str, int]


def _guidance_for(item: Dict) -> Tuple[str, str]:
    dg = item.get("decision_guidance", {}) or {}
    return dg.get("on_fail", "ESCALATE"), dg.get("on_uncertain", "ESCALATE")


def decide(
    checklist: Dict,
    results: List[Dict],
    *,
    tau_uncertain_rate: float = 0.25
) -> DecisionSummary:
    """
    Deterministic, auditable decisioning.
    - Hard stops based on item-level decision_guidance and CRITICAL severity.
    - Otherwise escalates when uncertainty is non-trivial.
    - Only recommends approval when all mandatory items are PASS.
    """

    items_by_id = {it["id"]: it for it in checklist["items"]}

    n = max(len(results), 1)
    n_pass = 0
    n_fail = 0
    n_uncertain = 0

    reasons: List[str] = []

    # Hard-stop flags
    must_refuse = False
    must_escalate = False

    for r in results:
        item_id = r["item_id"]
        status = r["status"]
        item = items_by_id.get(item_id, {})
        severity = item.get("severity", r.get("severity", "MEDIUM"))
        on_fail, on_uncertain = _guidance_for(item)

        if status == "PASS":
            n_pass += 1
            continue

        if status == "FAIL":
            n_fail += 1
            if severity == "CRITICAL" and on_fail == "REFUSE":
                must_refuse = True
                reasons.append(f"{item_id}: CRITICAL fail requires REFUSE.")
            else:
                must_escalate = True
                reasons.append(f"{item_id}: fail requires review ({on_fail}).")

        elif status == "UNCERTAIN":
            n_uncertain += 1
            if on_uncertain == "REFUSE":
                must_refuse = True
                reasons.append(f"{item_id}: UNCERTAIN requires REFUSE (insufficient info).")
            else:
                must_escalate = True
                reasons.append(f"{item_id}: UNCERTAIN requires escalation.")

        else:
            # Unknown status should never silently approve
            must_escalate = True
            reasons.append(f"{item_id}: unknown status '{status}' -> ESCALATE.")

    uncertain_rate = n_uncertain / n

    # Global uncertainty gate
    if uncertain_rate > tau_uncertain_rate:
        must_escalate = True
        reasons.append(f"Uncertain rate {uncertain_rate:.2f} exceeds threshold {tau_uncertain_rate:.2f}.")

    if must_refuse:
        decision: Decision = "REFUSE"
    elif must_escalate:
        decision = "ESCALATE"
    else:
        decision = "RECOMMEND_APPROVE"

    # Simple confidence proxy (deterministic, monotonic)
    # Weight fails higher than uncertain; keep in [0, 1].
    confidence = max(0.0, min(1.0, 1.0 - (2.0 * n_fail + 1.0 * n_uncertain) / n))

    return DecisionSummary(
        decision=decision,
        confidence=confidence,
        reasons=reasons,
        stats={
            "n_items": n,
            "n_pass": n_pass,
            "n_fail": n_fail,
            "n_uncertain": n_uncertain,
        },
    )
