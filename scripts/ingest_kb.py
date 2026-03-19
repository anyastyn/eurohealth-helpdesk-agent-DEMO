"""Build a persistent KB index for the EuroHealth helpdesk agent.

What this script does:
- Reads helpdesk documents from the configured knowledge folders
- Splits them into chunks
- Creates embeddings with OpenAI
- Writes a reusable JSON index to data/kb_index.json

Why it matters:
- Retrieval becomes more semantic and less keyword-only
- The API starts faster because it can reuse the saved index
- The project looks more like a real RAG pipeline
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openai import OpenAI

from src.config import Settings
from src.monitoring import AuditLogger
from src.retriever import LocalKnowledgeRetriever


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    settings = Settings.load()
    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is missing in .env")

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    logger = AuditLogger(settings.ingest_log_path)

    retriever = LocalKnowledgeRetriever(
        knowledge_dirs=settings.knowledge_dirs,
        chunk_size=settings.chunk_size,
    )
    if not retriever.documents:
        raise SystemExit("No source documents found for ingestion.")

    chunks = [doc.text for doc in retriever.documents]
    embeddings: list[list[float]] = []
    batch_size = 32
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        embeddings.extend([item.embedding for item in response.data])

    payload = {
        "schema_version": "eurohealth-kb-index-v1",
        "created_at": utc_now_iso(),
        "embedding_model": settings.embedding_model,
        "chunk_count": len(retriever.documents),
        "chunks": [
            {
                "source_id": document.source_id,
                "path": document.path,
                "text": document.text,
                "tokens": sorted(document.tokens),
                "embedding": embedding,
            }
            for document, embedding in zip(retriever.documents, embeddings)
        ],
    }

    settings.kb_index_path.parent.mkdir(parents=True, exist_ok=True)
    settings.kb_index_path.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.write(
        {
            "event": "kb_ingest_complete",
            "kb_index_path": str(settings.kb_index_path),
            "chunk_count": len(retriever.documents),
            "embedding_model": settings.embedding_model,
        }
    )
    print(f"Wrote KB index to {settings.kb_index_path}")
    print(f"Indexed {len(retriever.documents)} chunks")


if __name__ == "__main__":
    main()
