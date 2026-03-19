from src.policy_engine import PolicyDecisionPoint, PolicyEnforcementPoint


def test_hr_scope_is_redirected():
    pdp = PolicyDecisionPoint("governance/policies")
    pep = PolicyEnforcementPoint(pdp, audit_log_path="logs/test-policy-audit.jsonl")

    result = pep.enforce(
        query="Can you explain EuroHealth salary bands?",
        response="Salary bands are confidential.",
        confidence=0.9,
    )

    assert result["blocked"] is True
    assert result["policy_action"] == "redirect"


def test_pii_response_is_blocked():
    pdp = PolicyDecisionPoint("governance/policies")
    pep = PolicyEnforcementPoint(pdp, audit_log_path="logs/test-policy-audit.jsonl")

    result = pep.enforce(
        query="What is John Smith's salary?",
        response="John Smith earns 10000 EUR.",
        confidence=0.8,
    )

    assert result["blocked"] is True
    assert result["policy_action"] == "block"
