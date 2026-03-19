"""Knowledge retrieval for the EuroHealth agent."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import html
import re
from typing import Any

from openai import OpenAI

TOKEN_RE = re.compile(r"[a-zA-Z0-9]{2,}")
TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class SearchResult:
    """Single retrieved document chunk."""

    source_id: str
    path: str
    score: float
    snippet: str


@dataclass(frozen=True)
class IndexedChunk:
    """Indexable chunk with optional embedding."""

    source_id: str
    path: str
    text: str
    tokens: set[str]
    embedding: list[float] | None = None


class LocalKnowledgeRetriever:
    """Retriever backed by a saved KB index, with lexical fallback."""

    def __init__(
        self,
        knowledge_dirs: list[Path],
        chunk_size: int = 1200,
        index_path: Path | None = None,
        openai_client: OpenAI | None = None,
        embedding_model: str | None = None,
    ):
        self.chunk_size = chunk_size
        self.index_path = index_path
        self.openai_client = openai_client
        self.embedding_model = embedding_model
        self.documents = self._load_or_build_index(knowledge_dirs)

    @property
    def document_count(self) -> int:
        return len(self.documents)

    def search(self, query: str, top_k: int = 4) -> list[SearchResult]:
        """Retrieve the most relevant chunks for a user query."""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        query_embedding = self._embed_query(query)
        ranked = self._rank_documents(query_tokens, query_embedding)
        return ranked[:top_k]

    def _rank_documents(
        self,
        query_tokens: set[str],
        query_embedding: list[float] | None,
    ) -> list[SearchResult]:
        ranked: list[SearchResult] = []
        for document in self.documents:
            overlap = query_tokens & document.tokens
            lexical_score = len(overlap) / max(len(query_tokens), 1)
            semantic_score = 0.0
            if query_embedding and document.embedding:
                semantic_score = self._cosine_similarity(query_embedding, document.embedding)

            score = round((semantic_score * 0.75) + (lexical_score * 0.25), 2)
            if score <= 0:
                continue

            ranked.append(
                SearchResult(
                    source_id=document.source_id,
                    path=document.path,
                    score=score,
                    snippet=document.text[:700].strip(),
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked

    def _load_or_build_index(self, knowledge_dirs: list[Path]) -> list[IndexedChunk]:
        if self.index_path and self.index_path.exists():
            return self._load_saved_index(self.index_path)
        return self._build_index(knowledge_dirs)

    def _load_saved_index(self, index_path: Path) -> list[IndexedChunk]:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        return [
            IndexedChunk(
                source_id=item["source_id"],
                path=item["path"],
                text=item["text"],
                tokens=set(item["tokens"]),
                embedding=item.get("embedding"),
            )
            for item in payload.get("chunks", [])
        ]

    def _build_index(self, knowledge_dirs: list[Path]) -> list[IndexedChunk]:
        """Read supported files and split them into chunks."""
        documents: list[IndexedChunk] = []
        for directory in knowledge_dirs:
            if not directory.exists():
                continue

            for path in directory.rglob("*"):
                if path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".json", ".html"}:
                    continue

                text = self._read_text(path)
                if not text:
                    continue

                for index, chunk in enumerate(self._chunk_text(text), start=1):
                    source_id = f"{path.stem}-{index}"
                    documents.append(
                        IndexedChunk(
                            source_id=source_id,
                            path=str(path),
                            text=chunk,
                            tokens=self._tokenize(chunk),
                        )
                    )

        return documents

    def _read_text(self, path: Path) -> str:
        """Read a document and normalize it to plain text."""
        raw = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() == ".html":
            raw = TAG_RE.sub(" ", raw)
            raw = html.unescape(raw)
        return re.sub(r"\s+", " ", raw).strip()

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into fixed-size chunks."""
        if len(text) <= self.chunk_size:
            return [text]

        return [
            text[i : i + self.chunk_size]
            for i in range(0, len(text), self.chunk_size)
        ]

    def _embed_query(self, query: str) -> list[float] | None:
        if not self.openai_client or not self.embedding_model:
            return None

        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=[query],
        )
        return response.data[0].embedding

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
        right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
        return dot / (left_norm * right_norm)

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {token.lower() for token in TOKEN_RE.findall(text)}
