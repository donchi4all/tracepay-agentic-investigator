"""Observable event logging; contains no hidden chain-of-thought."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .safety import redact


class TrajectoryRecorder:
    def __init__(self, path: Optional[Path]):
        self.path = Path(path) if path else None
        self.sequence = 0
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")

    def record(
        self,
        agent: str,
        event: str,
        action: str,
        rationale: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.sequence += 1
        item = {
            "sequence": self.sequence,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "agent": agent,
            "event": event,
            "action": action,
            "rationale": rationale,
            # Defense in depth: callers should pass concise metadata, but the
            # recorder independently redacts secrets, PII-like values, and
            # local home paths before persistence.
            "details": redact(details or {}),
        }
        if self.path:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(item, sort_keys=True) + "\n")
