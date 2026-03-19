"""
EuroHealth AI Helpdesk — Policy Tests
=======================================

Tests that policy rules work as expected.
Part of CI/CD pipeline — must pass before deployment.

AI-DS + AI-SEC co-own this component.
"""

# TODO: AI-DS designs the evaluation framework
# TODO: AI-SEC defines policy test cases
#
# Example test cases:
#   - Salary query → MUST be blocked
#   - Normal IT query → MUST be allowed
#   - Low confidence response → MUST escalate
#   - Out-of-scope query → MUST redirect
#   - Same query in EN/DE/CZ → MUST get same policy decision
