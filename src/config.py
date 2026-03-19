"""Configuration for the EuroHealth cloud agent."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    openai_api_key: str | None
    openai_model: str
    embedding_model: str
    openai_base_url: str | None
    policy_dir: Path
    audit_log_path: Path
    runtime_log_path: Path
    ingest_log_path: Path
    kb_index_path: Path
    knowledge_dirs: list[Path]
    max_context_docs: int
    chunk_size: int
    port: int

    @staticmethod
    def load() -> "Settings":
        load_dotenv(override=False)
        root = Path(__file__).resolve().parent.parent

        raw_dirs = os.getenv("EUROHEALTH_KB_DIRS", "data/helpdesk,governance/policies")
        knowledge_dirs = [
            (root / item.strip()).resolve()
            for item in raw_dirs.split(",")
            if item.strip()
        ]

        return Settings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            policy_dir=(root / os.getenv("EUROHEALTH_POLICY_DIR", "governance/policies")).resolve(),
            audit_log_path=(root / os.getenv("EUROHEALTH_AUDIT_LOG", "logs/policy-audit.jsonl")).resolve(),
            runtime_log_path=(root / os.getenv("EUROHEALTH_RUNTIME_LOG", "logs/runtime-events.jsonl")).resolve(),
            ingest_log_path=(root / os.getenv("EUROHEALTH_INGEST_LOG", "logs/ingest-events.jsonl")).resolve(),
            kb_index_path=(root / os.getenv("EUROHEALTH_KB_INDEX", "data/kb_index.json")).resolve(),
            knowledge_dirs=knowledge_dirs,
            max_context_docs=int(os.getenv("EUROHEALTH_MAX_CONTEXT_DOCS", "4")),
            chunk_size=int(os.getenv("EUROHEALTH_CHUNK_SIZE", "1200")),
            port=int(os.getenv("PORT", "8000")),
        )
