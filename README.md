# EuroHealth Helpdesk Agent

A portfolio-ready, cloud-backed AI helpdesk agent built with FastAPI and OpenAI.

## Why this project exists

This repository shows how to build a small but realistic agentic AI system, not just a single prompt. The agent retrieves knowledge from enterprise-style documents, grounds answers in that knowledge, applies policy checks, and returns structured API responses with logging and auditability.

## What it demonstrates

- OpenAI API integration with `.env`-based secret management
- retrieval-augmented generation over helpdesk documents
- a persistent ingestion step with chunking and embeddings
- policy enforcement before answer delivery
- structured runtime and audit logging
- Docker-ready deployment
- browser demo page and API endpoints

## Architecture

User request -> retrieval -> grounded OpenAI answer draft -> policy check -> JSON response -> logs

## Main features

- `GET /`: lightweight browser demo page
- `GET /health`: health check endpoint
- `POST /chat`: structured chat endpoint
- `scripts/ingest_kb.py`: builds `data/kb_index.json` from source documents
- `scripts/audit_kb.py`: checks source documents for dirty-data signals

## What Each Main File Is For

- `main.py`: the smallest possible entrypoint that lets Uvicorn start the app.
- `src/agent.py`: the main orchestration layer. It receives the user question, retrieves context, calls OpenAI, applies policies, and returns the final API response.
- `src/retriever.py`: the retrieval layer. It loads the saved knowledge index and ranks chunks by semantic and keyword relevance.
- `src/policy_engine.py`: the runtime guardrail layer. It blocks, redirects, or escalates unsafe answers.
- `src/config.py`: loads environment variables from `.env` and resolves important project paths.
- `src/monitoring.py`: writes JSONL logs for runtime and audit events.
- `scripts/ingest_kb.py`: builds the reusable knowledge-base index from the source documents.
- `scripts/audit_kb.py`: checks the knowledge sources for dirty-data signals such as stale review dates or encoding issues.
- `data/helpdesk/`: realistic sample helpdesk knowledge articles used by retrieval.
- `governance/policies/`: YAML policy rules used by the policy engine.
- `docs/demo-ui.html`: a minimal browser UI for local demos.

## Quick start

1. Copy `.env.example` to `.env`
2. Add your `OPENAI_API_KEY`
3. Install dependencies
4. Build the KB index
5. Run the API

```powershell
pip install -r requirements.txt
python scripts/ingest_kb.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open:
- `http://localhost:8000/`
- `http://localhost:8000/docs`

## Example API test

```powershell
$body = @{
  question = "How do I access VPN at EuroHealth?"
  language = "EN"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8000/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## How Someone Can Try This Agent

1. Clone the repository
2. Create `.env` from `.env.example`
3. Add a valid `OPENAI_API_KEY`
4. Install dependencies
5. Build the KB index
6. Start the API
7. Open `http://localhost:8000/` in a browser or call the API directly

PowerShell commands:

```powershell
pip install -r requirements.txt
python scripts/ingest_kb.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

Suggested demo prompts:
- `How do I access VPN at EuroHealth?`
- `How do I reset my EuroHealth password?`
- `How do I re-enroll MFA after changing my phone?`
- `How do I install approved software?`
- `What is John Smith's salary?`

Expected behavior:
- IT helpdesk questions should return grounded step-by-step answers
- sensitive personal-data questions should be blocked or redirected
- weakly grounded questions should get a cautious answer instead of hallucination

## Project structure

- `src/`: runtime application code
- `scripts/`: ingestion and quality audit scripts
- `data/helpdesk/`: realistic sample helpdesk knowledge
- `governance/policies/`: policy-as-code rules
- `docs/agent-overview.md`: plain-English explanation of the agent
- `tests/`: unit and API tests

## Dirty data handling

Yes, the project includes dirty-data risk, because enterprise knowledge bases often contain:
- outdated procedures
- duplicate content
- missing metadata
- encoding issues
- irrelevant architecture docs mixed with operational content

Use this to audit the KB:

```powershell
python scripts/audit_kb.py
```

It writes a simple report to `data/kb_quality_report.json`.

For the public portfolio version, the agent is configured to use the cleaner support content in `data/helpdesk/` plus governance policies. The broader academy documentation is still in the repo as background material, but it is no longer the default live knowledge base. This keeps the dirty-data story visible without making the demo answers worse.

## Why this is portfolio-safe

- no secrets are committed
- generated logs and indexes are git-ignored
- the support documents are fictional demo content
- the repo is clearly positioned as a demo/portfolio agent, not a production healthcare platform

## Suggested next improvements

- replace file-based indexing with a real vector database
- add multilingual retrieval and answer evaluation
- connect human handoff to a ticketing system
- strengthen policy coverage and tests
- add CI for automated quality checks
