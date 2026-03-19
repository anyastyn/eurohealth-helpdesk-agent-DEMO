"""Runtime logging for the EuroHealth agent."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path


class AuditLogger:
    """Writes JSONL runtime events for troubleshooting and audit."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, payload: dict) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
