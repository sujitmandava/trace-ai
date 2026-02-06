from trace_ai.checklists.evaluator import evaluate_checklist


class _StubRetriever:
    def __init__(self, doc_results, policy_results):
        self._doc_results = doc_results
        self._policy_results = policy_results

    def retrieve(self, doc_query, policy_query=None, doc_id=None):
        return {
            "document_evidence": self._doc_results,
            "policy_evidence": self._policy_results,
        }


def test_checklist_eval_pass_with_doc_evidence():
    checklist = {
        "items": [
            {
                "id": "C-PAY-001",
                "title": "Payment Terms",
                "severity": "CRITICAL",
                "requirement": "Must include payment terms",
                "evidence_queries": {
                    "doc_query": "payment terms",
                    "policy_query": "payment policy",
                },
                "pass_criteria": "Payment terms are present.",
                "expected_evidence": {"min_quotes": 1, "must_include_terms": ["payment"]},
            }
        ]
    }

    doc_results = [
        {
            "metadata": {
                "chunk_id": "c1",
                "doc_id": "doc-1",
                "text": "Payment terms: customer pays within 30 days.",
            },
            "score": 0.9,
        }
    ]
    policy_results = [
        {
            "metadata": {
                "chunk_id": "p1",
                "doc_id": "policy-1",
                "text": "Policy: payment terms must be specified.",
            },
            "score": 0.8,
        }
    ]

    retriever = _StubRetriever(doc_results, policy_results)
    results = evaluate_checklist(checklist, retriever, doc_id="doc-1")

    assert results[0]["status"] == "PASS"
    assert any(c["source"] == "document" for c in results[0]["citations"])
    assert any(c["source"] == "policy" for c in results[0]["citations"])


def test_checklist_eval_fail_when_no_doc_evidence():
    checklist = {
        "items": [
            {
                "id": "C-PARTIES-001",
                "title": "Parties Identified",
                "severity": "CRITICAL",
                "requirement": "Must identify parties",
                "evidence_queries": {"doc_query": "between"},
                "pass_criteria": "Parties are stated.",
                "expected_evidence": {"min_quotes": 1},
            }
        ]
    }

    doc_results = []
    policy_results = [
        {
            "metadata": {
                "chunk_id": "p2",
                "doc_id": "policy-1",
                "text": "Policy: parties must be identified.",
            },
            "score": 0.7,
        }
    ]

    retriever = _StubRetriever(doc_results, policy_results)
    results = evaluate_checklist(checklist, retriever, doc_id="doc-1")

    assert results[0]["status"] == "FAIL"
    assert all(c["source"] == "policy" for c in results[0]["citations"])
