# Policy-as-Code (YAML) — EuroHealth Helpdesk Agent (MVP)

These YAML files are **starter governance rules** for the EuroHealth on‑prem helpdesk agent.
They are written to be used by a **Policy Decision Point (PDP)** and enforced by a **Policy Enforcement Point (PEP)**.

**How to use (Day 16 / MVP):**
- Treat these as the source of truth for what the agent is allowed to do.
- The PDP evaluates rules against the request/response context.
- The PEP applies the enforcement action (ALLOW / BLOCK / REDIRECT / ESCALATE) and logs an audit record.

**Design assumptions (from Week 4 scenario):**
- On‑prem only (Phase 1), EU context
- High‑risk classification under EU AI Act (Annex III), readiness by **Aug 2, 2026**
- No employee PII in training data; strict PII protection in responses
- Languages: EN / DE / CZ
- Phase 1 scope: **IT helpdesk only** (no HR/Claims/Finance actions)

Generated: 2026-03-03
