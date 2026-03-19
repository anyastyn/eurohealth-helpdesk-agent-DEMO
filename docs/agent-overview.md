# EuroHealth Helpdesk Agent Overview

## What this project is

This project is a cloud-backed AI helpdesk agent for EuroHealth. It runs as a FastAPI service, uses OpenAI models for reasoning and embeddings, retrieves local knowledge-base content, and applies policy checks before returning an answer.

It is designed as a portfolio project that shows:
- agent runtime design
- retrieval-augmented generation
- policy enforcement
- logging and auditability
- container readiness

## High-level logic

1. A user sends a JSON request to `/chat`.
2. The app retrieves the most relevant helpdesk knowledge chunks.
3. The app sends the user question plus retrieved context to OpenAI.
4. The language model drafts an answer.
5. The policy engine checks whether the answer is safe and in scope.
6. The API returns the final answer together with confidence, sources, and policy metadata.
7. Runtime and policy decisions are written to logs.

## Why there is also an ingestion script

The ingestion script builds a reusable knowledge-base index. This makes retrieval more realistic because the system stores chunked documents and embeddings instead of reading and searching raw files from scratch every time.

## Main files and why they exist

- `main.py`: minimal application entrypoint used by Uvicorn and Docker.
- `src/agent.py`: main orchestration logic for retrieval, LLM call, policy enforcement, and API routes.
- `src/retriever.py`: retrieval layer that loads the saved KB index and ranks chunks using embeddings and lexical overlap.
- `src/policy_engine.py`: policy decision and enforcement layer.
- `src/config.py`: loads `.env` settings and resolves project paths.
- `src/monitoring.py`: writes structured JSONL logs.
- `scripts/ingest_kb.py`: prepares chunked documents and embeddings for retrieval.
- `data/helpdesk/*.md`: realistic sample support knowledge articles.
- `governance/policies/*.yaml`: policy rules used by the runtime safety layer.
- `Dockerfile`: container recipe for local Docker run or cloud deployment.
- `docker-compose.yml`: convenience file for local container startup.

## What makes it "agentic"

This is not only a plain chat completion. The system performs a sequence of controlled steps:
- reads environment and runtime configuration
- retrieves supporting knowledge
- grounds the prompt in enterprise documents
- applies policy checks
- logs decisions for traceability

That combination of orchestration, external knowledge use, and governance is what makes it a practical agentic AI demo rather than just a single prompt.

## Current limitations

- retrieval is still intentionally lightweight and file-based
- the policy engine uses simplified matching rules
- there is no user interface yet
- tests are still minimal
- no human handoff backend is connected yet
