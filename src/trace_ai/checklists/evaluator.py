# src/trace_ai/checklists/evaluator.py

from typing import Dict, List
from trace_ai.retrieval.reranker import rerank


def _contains_any(text: str, terms: List[str]) -> bool:
    t = text.lower()
    return any(term.lower() in t for term in terms)


def evaluate_item(
    item: Dict,
    retrieved: Dict,
    min_score: float = 0.3,
    *,
    verbose: bool = False
) -> Dict:
    if verbose:
        print("------EVALUATE ITEM------")

    doc_results = retrieved.get("document_evidence", [])
    policy_results = retrieved.get("policy_evidence", [])
    expected = item.get("expected_evidence", {})
    must_include = expected.get("must_include_terms", [])
    must_exclude = expected.get("must_exclude_terms", [])
    min_quotes = expected.get("min_quotes", 1)
    if verbose:
        print(f"expected: {expected}")

    def _to_citation(r: Dict, source: str) -> Dict:
        meta = r["metadata"]
        return {
            "chunk_id": meta.get("chunk_id"),
            "doc_id": meta.get("doc_id"),
            "quote": meta.get("text", "")[:500],
            "score": r["score"],
            "source": source,
        }

    doc_citations: List[Dict] = []
    policy_citations: List[Dict] = []

    if doc_results:
        ranked = rerank(item["evidence_queries"]["doc_query"], doc_results)
        if verbose:
            for r in ranked:
                print(r)

        for r in ranked:
            if r["score"] < min_score:
                continue

            text = r["metadata"]["text"]

            if must_exclude and _contains_any(text, must_exclude):
                return {
                    "status": "FAIL",
                    "rationale": f"Excluded terms present: {must_exclude}",
                    "citations": [_to_citation(r, "document")]
                }

            doc_citations.append(_to_citation(r, "document"))

    policy_query = item["evidence_queries"].get("policy_query") or item["evidence_queries"]["doc_query"]
    if policy_results:
        policy_ranked = rerank(policy_query, policy_results)
        for r in policy_ranked:
            if r["score"] < min_score:
                continue
            policy_citations.append(_to_citation(r, "policy"))

    # No document evidence at all: cannot pass, but attach policy context if any
    if not doc_citations:
        return {
            "status": "FAIL" if item["severity"] == "CRITICAL" else "UNCERTAIN",
            "rationale": "No supporting evidence found in document.",
            "citations": policy_citations
        }

    if len(doc_citations) < min_quotes:
        return {
            "status": "FAIL" if item["severity"] == "CRITICAL" else "UNCERTAIN",
            "rationale": "Insufficient evidence to satisfy requirement.",
            "citations": doc_citations + policy_citations
        }

    if must_include:
        combined = " ".join(c["quote"] for c in doc_citations)
        if not _contains_any(combined, must_include):
            return {
                "status": "FAIL",
                "rationale": f"Required terms missing: {must_include}",
                "citations": doc_citations + policy_citations
            }

    return {
        "status": "PASS",
        "rationale": item["pass_criteria"],
        "citations": doc_citations + policy_citations
    }


def evaluate_checklist(
    checklist: Dict,
    retriever,
    doc_id,
    *,
    verbose: bool = False
) -> List[Dict]:
    results = []
    if verbose:
        print("------EVALUATE CHECKLIST------")
    for item in checklist["items"]:
        if verbose:
            print(f"\nCurrent Item: {item['evidence_queries']}")
        evidence = retriever.retrieve(
            doc_query=item["evidence_queries"]["doc_query"],
            policy_query=item["evidence_queries"].get("policy_query"),
            doc_id=doc_id
        )
        # print(f"Evidence retrieved for item {item}: {evidence}")

        for e in evidence["document_evidence"]:
            assert e["metadata"]["doc_id"] == doc_id

        item_result = evaluate_item(item, evidence, verbose=verbose)

        results.append({
            "item_id": item["id"],
            "title": item["title"],
            "severity": item["severity"],
            "status": item_result["status"],
            "rationale": item_result["rationale"],
            "citations": item_result["citations"]
        })

    return results
