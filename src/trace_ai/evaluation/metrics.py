from typing import Dict, List

def decision_accuracy(expected: str, actual: str) -> bool:
    return expected == actual


def false_approval(expected: str, actual: str) -> bool:
    """
    Worst-case error: system approved when it should not.
    """
    return actual == "RECOMMEND_APPROVE" and expected != "RECOMMEND_APPROVE"


def missed_critical_items(
    expected_missing: List[str],
    results: List[Dict]
) -> List[str]:
    """
    Returns CRITICAL items that should have failed but did not.
    """
    missed = []
    for r in results:
        if r["item_id"] in expected_missing and r["status"] == "PASS":
            missed.append(r["item_id"])
    return missed
