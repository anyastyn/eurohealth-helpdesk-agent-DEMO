"""Policy decision and enforcement for the EuroHealth agent."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

import yaml


EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
PHONE_RE = re.compile(r"\+\d[\d\s-]{6,}")
ID_RE = re.compile(r"\b\d{6,}\b")
SALARY_RE = re.compile(r"\b\d[\d,\. ]*\s?(eur|usd|czk|salary)\b", re.IGNORECASE)

INTENT_KEYWORDS = {
    "hr": ["salary", "benefit", "benefits", "leave", "parental", "hr"],
    "claims": ["claim", "claims", "reimbursement"],
    "finance": ["invoice", "finance", "budget", "payment"],
}


class PolicyDecisionPoint:
    """Loads YAML policies and returns the first matching decision."""

    def __init__(self, policies_dir: str):
        self.policies: list[dict] = []
        self.load_policies(policies_dir)

    def load_policies(self, policies_dir: str) -> None:
        base = Path(policies_dir)
        if not base.exists():
            return

        for filepath in sorted(base.glob("*.y*ml")):
            with filepath.open(encoding="utf-8") as handle:
                policy = yaml.safe_load(handle) or {}
            self.policies.append({"path": str(filepath), "data": policy})

    def evaluate(self, query: str, response: str, confidence: float = 1.0) -> dict:
        """Evaluate the query and response against loaded policies."""
        for wrapper in self.policies:
            policy = wrapper["data"]
            policy_name = self._policy_name(policy, wrapper["path"])
            for rule in self._rules(policy):
                if self._rule_matches(rule, query, response, confidence):
                    return self._decision_from_rule(policy_name, rule)

        return {
            "decision": "allow",
            "policy": None,
            "rule_id": None,
            "reason": None,
            "substitute": None,
            "escalate_to": None,
        }

    def _decision_from_rule(self, policy_name: str, rule: dict) -> dict:
        rule_id = rule.get("id") or rule.get("rule_id")

        if "then" in rule and isinstance(rule["then"], dict):
            action = str(rule["then"].get("action", "allow")).lower()
            return {
                "decision": self._normalize_action(action),
                "policy": policy_name,
                "rule_id": rule_id,
                "reason": rule["then"].get("reason"),
                "substitute": rule["then"].get("user_message"),
                "escalate_to": rule["then"].get("escalate_to"),
            }

        if "then" in rule:
            return {
                "decision": self._normalize_action(str(rule["then"])),
                "policy": policy_name,
                "rule_id": rule_id,
                "reason": rule.get("log"),
                "substitute": rule.get("respond") or rule.get("substitute"),
                "escalate_to": rule.get("escalate_to"),
            }

        return {
            "decision": "allow",
            "policy": policy_name,
            "rule_id": rule_id,
            "reason": None,
            "substitute": None,
            "escalate_to": None,
        }

    def _rule_matches(
        self,
        rule: dict,
        query: str,
        response: str,
        confidence: float,
    ) -> bool:
        if "if" not in rule:
            return False

        condition = rule["if"]

        if isinstance(condition, str):
            return self._matches_string_condition(condition, query, response, confidence)

        if isinstance(condition, dict):
            return self._matches_dict_condition(condition, query, response, confidence)

        return False

    def _matches_string_condition(
        self,
        condition: str,
        query: str,
        response: str,
        confidence: float,
    ) -> bool:
        lowered = condition.lower()

        if "response.contains" in lowered:
            raw = lowered.split("(", 1)[1].rstrip(")")
            keywords = [item.strip() for item in raw.split(",")]
            return any(keyword and keyword in response.lower() for keyword in keywords)

        if "query.contains" in lowered:
            raw = lowered.split("(", 1)[1].rstrip(")")
            keywords = [item.strip() for item in raw.split(",")]
            return any(keyword and keyword in query.lower() for keyword in keywords)

        if "confidence" in lowered and "<" in lowered:
            try:
                threshold = float(lowered.split("<", 1)[1].strip())
            except ValueError:
                return False
            return confidence < threshold

        return False

    def _matches_dict_condition(
        self,
        condition: dict,
        query: str,
        response: str,
        confidence: float,
    ) -> bool:
        if "model_confidence_less_than" in condition:
            return confidence < float(condition["model_confidence_less_than"])

        if "user_intent_in" in condition:
            intents = condition["user_intent_in"]
            return any(self._intent_matches(intent, query) for intent in intents)

        if "response_contains" in condition:
            categories = condition["response_contains"].get("pii_categories", [])
            return any(self._pii_category_matches(category, response) for category in categories)

        if "user_input_contains" in condition:
            categories = condition["user_input_contains"].get("pii_categories", [])
            return any(self._pii_category_matches(category, query) for category in categories)

        return False

    @staticmethod
    def _intent_matches(intent: str, query: str) -> bool:
        return any(word in query.lower() for word in INTENT_KEYWORDS.get(intent, [intent]))

    @staticmethod
    def _pii_category_matches(category: str, text: str) -> bool:
        lowered = text.lower()
        if category == "email":
            return bool(EMAIL_RE.search(text))
        if category == "phone":
            return bool(PHONE_RE.search(text))
        if category == "national_id":
            return bool(ID_RE.search(text))
        if category == "salary":
            return bool(SALARY_RE.search(text)) or "salary" in lowered
        if category == "medical_info":
            return any(word in lowered for word in ["diagnosis", "medical", "health record"])
        if category == "address":
            return "address" in lowered
        if category == "person_name":
            return any(
                phrase in lowered
                for phrase in ["john smith", "employee name", "full name", "mr.", "ms."]
            )
        return False

    @staticmethod
    def _policy_name(policy: dict, fallback_path: str) -> str:
        if "policy" in policy:
            return str(policy["policy"].get("name", Path(fallback_path).stem))
        if "policy_set" in policy:
            return str(policy["policy_set"])
        return Path(fallback_path).stem

    @staticmethod
    def _rules(policy: dict) -> list[dict]:
        if "policy" in policy:
            return policy["policy"].get("rules", [])
        return policy.get("rules", [])

    @staticmethod
    def _normalize_action(action: str) -> str:
        mapping = {
            "block": "block",
            "redirect": "redirect",
            "escalate": "escalate",
            "allow": "allow",
        }
        return mapping.get(action.lower(), "allow")


class PolicyEnforcementPoint:
    """Enforces policy decisions and writes audit logs."""

    def __init__(self, pdp: PolicyDecisionPoint, audit_log_path: str = "audit.log"):
        self.pdp = pdp
        self.audit_log_path = audit_log_path

    def enforce(self, query: str, response: str, confidence: float = 1.0) -> dict:
        decision = self.pdp.evaluate(query, response, confidence)
        self._write_audit_log(query, decision)

        if decision["decision"] == "allow":
            return {"response": response, "blocked": False, "policy_action": "allow"}

        substitute = decision.get("substitute")
        if not substitute:
            substitute = {
                "block": "Request blocked by policy.",
                "redirect": "This request is outside my scope. Please use the official support channel.",
                "escalate": "I am not confident enough to answer safely. Please contact a human agent.",
            }.get(decision["decision"], "Request blocked by policy.")

        return {
            "response": substitute,
            "blocked": True,
            "policy_action": decision["decision"],
            "policy": decision["policy"],
            "rule_id": decision["rule_id"],
            "reason": decision["reason"],
            "escalated_to": decision.get("escalate_to"),
        }

    def _write_audit_log(self, query: str, decision: dict) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_hash": hash(query) % 10**8,
            "decision": decision["decision"],
            "policy": decision.get("policy"),
            "rule_id": decision.get("rule_id"),
            "reason": decision.get("reason"),
        }

        os.makedirs(Path(self.audit_log_path).parent or ".", exist_ok=True)
        with open(self.audit_log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
