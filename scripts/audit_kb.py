"""Audit source knowledge for dirty-data signals."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import Settings

DATE_RE = re.compile(r"Last reviewed:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
MOJIBAKE_MARKERS = ["Ã", "â", "�"]


def main() -> None:
    settings = Settings.load()
    findings: list[dict] = []
    now = datetime.now(timezone.utc).date()

    for directory in settings.knowledge_dirs:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.suffix.lower() not in {".md", ".txt", ".html", ".yaml", ".yml", ".json"}:
                continue
            if path.name in {"kb_index.json", "kb_quality_report.json"}:
                continue

            text = path.read_text(encoding="utf-8", errors="ignore")
            issues: list[str] = []

            if any(marker in text for marker in MOJIBAKE_MARKERS):
                issues.append("possible_encoding_issue")

            match = DATE_RE.search(text)
            if match:
                reviewed = datetime.strptime(match.group(1), "%Y-%m-%d").date()
                if (now - reviewed).days > 365:
                    issues.append("stale_review_date")

            if "Last reviewed:" not in text and "data/helpdesk" in str(path).replace(chr(92), "/"):
                issues.append("missing_last_reviewed_metadata")

            if issues:
                findings.append({"path": str(path), "issues": issues})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "finding_count": len(findings),
        "findings": findings,
    }
    out_path = ROOT / "data" / "kb_quality_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote KB quality report to {out_path}")
    print(f"Found {len(findings)} documents with dirty-data signals")


if __name__ == "__main__":
    main()
