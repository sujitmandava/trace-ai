# src/trace_ai/checklists/evaluator.py

from typing import Dict, List
from trace_ai.retrieval.reranker import rerank


def _contains_any(text: str, terms: List[str]) -> bool:
    t = text.lower()
    return any(term.lower() in t for term in terms)


def evaluate_item(
    item: Dict,
    retrieved: Dict,
    min_score: float = 0.3
) -> Dict:

    doc_results = retrieved["document_evidence"]
    expected = item.get("expected_evidence", {})
    must_include = expected.get("must_include_terms", [])
    must_exclude = expected.get("must_exclude_terms", [])
    min_quotes = expected.get("min_quotes", 1)

    # No evidence at all
    if not doc_results:
        return {
            "status": "FAIL" if item["severity"] == "CRITICAL" else "UNCERTAIN",
            "rationale": "No supporting evidence found in document.",
            "citations": []
        }

    ranked = rerank(item["evidence_queries"]["doc_query"], doc_results)

    citations = []
    for r in ranked:
        if r["score"] <= min_score:
            continue

        text = r["metadata"]["text"]

        if must_exclude and _contains_any(text, must_exclude):
            return {
                "status": "FAIL",
                "rationale": f"Excluded terms present: {must_exclude}",
                "citations": [{
                    "chunk_id": r["metadata"]["chunk_id"],
                    "doc_id": r["metadata"]["doc_id"],
                    "quote": text[:500],
                    "score": r["score"]
                }]
            }

        citations.append({
            "chunk_id": r["metadata"]["chunk_id"],
            "doc_id": r["metadata"]["doc_id"],
            "quote": text[:500],
            "score": r["score"]
        })

    if len(citations) < min_quotes:
        return {
            "status": "FAIL" if item["severity"] == "CRITICAL" else "UNCERTAIN",
            "rationale": "Insufficient evidence to satisfy requirement.",
            "citations": citations
        }

    if must_include:
        combined = " ".join(c["quote"] for c in citations)
        if not _contains_any(combined, must_include):
            return {
                "status": "FAIL",
                "rationale": f"Required terms missing: {must_include}",
                "citations": citations
            }

    return {
        "status": "PASS",
        "rationale": item["pass_criteria"],
        "citations": citations
    }


def evaluate_checklist(
    checklist: Dict,
    retriever,
) -> List[Dict]:

    results = []

    for item in checklist["items"]:
        evidence = retriever.retrieve(
            doc_query=item["evidence_queries"]["doc_query"],
            policy_query=item["evidence_queries"].get("policy_query")
        )

        item_result = evaluate_item(item, evidence)

        results.append({
            "item_id": item["id"],
            "title": item["title"],
            "severity": item["severity"],
            "status": item_result["status"],
            "rationale": item_result["rationale"],
            "citations": item_result["citations"]
        })

    return results
