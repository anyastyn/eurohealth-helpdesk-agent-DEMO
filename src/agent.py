"""Cloud-backed EuroHealth helpdesk agent."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI
from pydantic import BaseModel, Field

from src.config import Settings
from src.monitoring import AuditLogger
from src.policy_engine import PolicyDecisionPoint, PolicyEnforcementPoint
from src.retriever import LocalKnowledgeRetriever, SearchResult


class ChatRequest(BaseModel):
    """Incoming agent request."""

    question: str = Field(min_length=3, max_length=4000)
    language: str = Field(default="EN", min_length=2, max_length=8)
    session_id: str | None = None


class SourceItem(BaseModel):
    """Response source metadata."""

    path: str
    score: float
    snippet: str


class ChatResponse(BaseModel):
    """Outgoing agent response."""

    decision_id: str
    answer: str
    language: str
    model_version: str
    retrieved_doc_ids: list[str]
    policy_decision: str
    confidence: float
    blocked: bool
    sources: list[SourceItem]
    meta: dict


class EuroHealthAgent:
    """Minimal production-style runtime for the EuroHealth helpdesk."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings.load()
        self.client = OpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
        )
        self.retriever = LocalKnowledgeRetriever(
            knowledge_dirs=self.settings.knowledge_dirs,
            chunk_size=self.settings.chunk_size,
            index_path=self.settings.kb_index_path,
            openai_client=self.client,
            embedding_model=self.settings.embedding_model,
        )
        self.pdp = PolicyDecisionPoint(str(self.settings.policy_dir))
        self.pep = PolicyEnforcementPoint(
            self.pdp,
            audit_log_path=str(self.settings.audit_log_path),
        )
        self.audit = AuditLogger(self.settings.runtime_log_path)

    def answer(self, request: ChatRequest) -> ChatResponse:
        """Answer a user question using local knowledge and OpenAI."""
        decision_id = str(uuid.uuid4())
        search_results = self.retriever.search(
            request.question,
            top_k=self.settings.max_context_docs,
        )
        confidence = self._estimate_confidence(search_results)

        if not search_results or search_results[0].score < 0.45:
            draft_answer = (
                "I could not find enough verified EuroHealth knowledge for that request. "
                "Please contact the human service desk so the question can be handled safely."
            )
        else:
            draft_answer = self._generate_answer(request, search_results)

        enforced = self.pep.enforce(
            query=request.question,
            response=draft_answer,
            confidence=confidence,
        )

        policy_decision = enforced["policy_action"].upper()
        final_answer = enforced["response"]
        blocked = enforced["blocked"]

        self.audit.write(
            {
                "decision_id": decision_id,
                "question": request.question,
                "language": request.language,
                "model_version": self.settings.openai_model,
                "policy_decision": policy_decision,
                "confidence": confidence,
                "retrieved_doc_ids": [result.source_id for result in search_results],
                "blocked": blocked,
                "session_id": request.session_id,
            }
        )

        return ChatResponse(
            decision_id=decision_id,
            answer=final_answer,
            language=request.language.upper(),
            model_version=self.settings.openai_model,
            retrieved_doc_ids=[result.source_id for result in search_results],
            policy_decision=policy_decision,
            confidence=confidence,
            blocked=blocked,
            sources=[
                SourceItem(
                    path=result.path,
                    score=result.score,
                    snippet=result.snippet,
                )
                for result in search_results
            ],
            meta={
                "policy_reason": enforced.get("reason"),
                "escalated_to": enforced.get("escalated_to"),
            },
        )

    def _generate_answer(
        self,
        request: ChatRequest,
        search_results: list[SearchResult],
    ) -> str:
        """Call the OpenAI API with strict grounding instructions."""
        context = "\n\n".join(
            f"[{item.source_id}] {item.snippet}" for item in search_results
        )
        system_prompt = (
            "You are the EuroHealth IT helpdesk assistant. "
            "Answer only with grounded information from the provided context. "
            "If the context is incomplete, say you are not confident and recommend a human handoff. "
            "Do not invent policies, access rights, dates, or employee data. "
            "Phase 1 scope is IT helpdesk only. "
            "Prefer concise step-by-step instructions when the knowledge base contains a procedure."
        )
        user_prompt = (
            f"Language: {request.language.upper()}\n"
            f"Question: {request.question}\n\n"
            f"Knowledge base context:\n{context}\n\n"
            "Write a concise helpdesk answer. Cite relevant source ids in plain text when useful."
        )

        response = self.client.responses.create(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = getattr(response, "output_text", "").strip()
        if text:
            return text

        try:
            return json.dumps(response.model_dump(), ensure_ascii=True)
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=502, detail="Model returned no text output") from exc

    @staticmethod
    def _estimate_confidence(search_results: list[SearchResult]) -> float:
        """Estimate answer confidence from retrieval quality."""
        if not search_results:
            return 0.25

        top_score = search_results[0].score
        doc_bonus = min(len(search_results), 3) * 0.12
        confidence = 0.15 + top_score + doc_bonus
        return round(min(confidence, 0.95), 2)


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    settings = Settings.load()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Create a .env file before starting the agent."
        )

    agent = EuroHealthAgent(settings)
    app = FastAPI(title="EuroHealth Helpdesk Agent", version="1.0.0")
    ui_path = Path(__file__).resolve().parent.parent / "docs" / "demo-ui.html"

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "model": settings.openai_model,
            "knowledge_docs": agent.retriever.document_count,
            "policy_dir": str(settings.policy_dir),
        }

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return ui_path.read_text(encoding="utf-8")

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        return agent.answer(request)

    return app


app = create_app()
