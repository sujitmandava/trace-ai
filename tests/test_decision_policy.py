from trace_ai.agent.decision_policy import decide


def test_decision_refuse_on_critical_fail():
    checklist = {
        "items": [
            {
                "id": "C-CRIT-001",
                "severity": "CRITICAL",
                "decision_guidance": {"on_fail": "REFUSE", "on_uncertain": "ESCALATE"},
            }
        ]
    }
    results = [{"item_id": "C-CRIT-001", "status": "FAIL"}]

    summary = decide(checklist, results, tau_uncertain_rate=0.25)

    assert summary.decision == "REFUSE"
    assert summary.stats["n_fail"] == 1


def test_decision_approve_when_all_pass():
    checklist = {
        "items": [
            {
                "id": "C-OK-001",
                "severity": "MEDIUM",
                "decision_guidance": {"on_fail": "ESCALATE", "on_uncertain": "ESCALATE"},
            }
        ]
    }
    results = [{"item_id": "C-OK-001", "status": "PASS"}]

    summary = decide(checklist, results, tau_uncertain_rate=0.25)

    assert summary.decision == "RECOMMEND_APPROVE"
