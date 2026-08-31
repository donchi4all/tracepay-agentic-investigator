"""Evidence collection, normalization, correlation, and redaction."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .models import EvidenceItem
from .repository import FixtureRepository
from .safety import find_untrusted_instruction_text, redact
from .trajectory import TrajectoryRecorder


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


class EvidenceCollector:
    def __init__(self, repository: FixtureRepository):
        self.repository = repository

    def collect(
        self, case_id: str, recorder: TrajectoryRecorder
    ) -> Tuple[Dict[str, Any], List[EvidenceItem], List[str]]:
        recorder.record(
            "evidence_collector",
            "instruction",
            "Search the synthetic fixture repository by case and transaction reference.",
            "The repository is the only allow-listed, read-only evidence source.",
            {"case_id": case_id},
        )
        case = self.repository.load_case(case_id)
        fixture_integrity = self.repository.integrity(case_id)
        reference = case["transaction_reference"]
        evidence: List[EvidenceItem] = []
        security_findings: List[str] = []

        for index, record in enumerate(case.get("records", []), 1):
            timestamp = record.get("timestamp")
            if not _valid_timestamp(timestamp):
                recorder.record(
                    "evidence_collector",
                    "validation_feedback",
                    "Reject malformed event timestamp and attempt the declared received_at fallback.",
                    "Timeline ordering requires a valid timestamp; fixture content cannot be trusted implicitly.",
                    {"record_id": record.get("record_id"), "invalid_timestamp": str(timestamp)},
                )
                fallback = record.get("received_at")
                if not _valid_timestamp(fallback):
                    recorder.record(
                        "evidence_collector",
                        "record_skipped",
                        "Skip record with no valid timestamp.",
                        "An invalid timestamp must not be invented.",
                        {"record_id": record.get("record_id")},
                    )
                    continue
                timestamp = fallback
                recorder.record(
                    "evidence_collector",
                    "retry_success",
                    "Use received_at as the explicit fallback timestamp.",
                    "The correction is fixture-provided and observable.",
                    {"record_id": record.get("record_id"), "timestamp": timestamp},
                )

            payload = redact(record.get("payload", {}))
            findings = find_untrusted_instruction_text(payload)
            if findings:
                security_findings.extend(
                    "%s:%s" % (record.get("record_id", "unknown"), path) for path in findings
                )
                recorder.record(
                    "evidence_collector",
                    "security_finding",
                    "Treat instruction-like log text as untrusted evidence data.",
                    "Log content is never an agent instruction and structural fields remain authoritative.",
                    {"record_id": record.get("record_id"), "paths": findings},
                )

            evidence.append(
                EvidenceItem(
                    evidence_id="EV-%s-%03d" % (case_id, index),
                    source_system=str(record.get("source_system", "unknown")),
                    record_id=str(record.get("record_id", "record-%d" % index)),
                    transaction_reference=reference,
                    timestamp=timestamp,
                    event_type=str(record.get("event_type", "UNKNOWN_EVENT")),
                    sanitized_payload=payload,
                    integrity="%s#record=%d" % (fixture_integrity, index),
                )
            )

        # Use the latest normalized fixture event as the evidence snapshot.
        # Empty lookups fall back to the frozen dataset timestamp. This keeps
        # regenerated reports deterministic without pretending a fixed value is
        # the wall-clock execution time.
        snapshot_timestamp = (
            max(item.timestamp for item in evidence)
            if evidence
            else self.repository.dataset_frozen_at()
        )
        evidence.append(
            EvidenceItem(
                evidence_id="EV-%s-SEARCH" % case_id,
                source_system="fixture_repository",
                record_id="search-%s" % case_id,
                transaction_reference=reference,
                timestamp=snapshot_timestamp,
                event_type="SEARCH_RESULT",
                sanitized_payload={
                    "matched_records": len(evidence),
                    "case_id": case_id,
                    "read_only": True,
                },
                integrity=fixture_integrity,
            )
        )
        recorder.record(
            "evidence_collector",
            "tool_response",
            "Return correlated and sanitized evidence.",
            "Every item now has source, record, timestamp, transaction reference, and integrity metadata.",
            {"evidence_count": len(evidence), "security_findings": len(security_findings)},
        )
        return case, evidence, security_findings
