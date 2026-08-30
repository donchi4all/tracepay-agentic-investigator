"""Frozen dataset and privacy validation."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .models import FailureClass
from .repository import FixtureRepository


REQUIRED_CATEGORIES = {
    "straightforward_authentication_failure",
    "initiator_count_limit",
    "initiator_amount_limit",
    "approver_amount_limit",
    "invalid_cba_response",
    "missing_transaction",
    "no_action_required_already_final",
    "empty_error_with_context",
    "timeout_ambiguous_downstream",
    "duplicate_request",
    "conflicting_evidence",
    "prompt_injection_in_log",
}
FORBIDDEN_TEXT = re.compile(
    r"https?://|prod(uction)?[._-]|BEGIN (RSA|OPENSSH) PRIVATE KEY|sk-[A-Za-z0-9]",
    re.IGNORECASE,
)


def _is_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def validate_dataset(project_root: Path) -> Dict[str, Any]:
    repository = FixtureRepository(project_root)
    definitions = repository.case_definitions()
    errors: List[str] = []
    seen_categories = set()
    seen_classes = set()
    fixture_hashes: Dict[str, str] = {}

    if len(definitions) < 12:
        errors.append("Expected at least 12 cases, found %d" % len(definitions))
    if len({item["case_id"] for item in definitions}) != len(definitions):
        errors.append("Case IDs are not unique")

    for definition in definitions:
        case_id = definition["case_id"]
        seen_categories.update(definition.get("categories", []))
        seen_classes.add(definition.get("gold", {}).get("failure_class"))
        try:
            case = repository.load_case(case_id)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append("%s: cannot load fixture: %s" % (case_id, exc))
            continue
        raw = json.dumps(case, sort_keys=True)
        if FORBIDDEN_TEXT.search(raw):
            errors.append("%s: possible endpoint, production marker, or credential" % case_id)
        if "gold" in case:
            errors.append("%s: gold labels must not appear in the evidence fixture" % case_id)
        if not str(case.get("transaction_reference", "")).startswith("TX-SYN-"):
            errors.append("%s: transaction reference is not explicitly synthetic" % case_id)
        record_ids = [record.get("record_id") for record in case.get("records", [])]
        if len(record_ids) != len(set(record_ids)):
            errors.append("%s: record IDs are not unique" % case_id)
        for record in case.get("records", []):
            required = {"source_system", "record_id", "timestamp", "event_type", "payload"}
            if not required.issubset(record):
                errors.append("%s/%s: missing record fields" % (case_id, record.get("record_id")))
            if not _is_timestamp(record.get("timestamp", "")) and not _is_timestamp(
                record.get("received_at", "")
            ):
                errors.append("%s/%s: no valid timestamp or fallback" % (case_id, record.get("record_id")))
            for key in ("pin", "otp", "token"):
                if key in record.get("payload", {}) and not str(record["payload"][key]).startswith(
                    "SYNTHETIC_"
                ):
                    errors.append("%s/%s: sensitive sentinel is not explicitly synthetic" % (case_id, key))
        fixture_hashes[case_id] = repository.integrity(case_id)

    missing_categories = sorted(REQUIRED_CATEGORIES - seen_categories)
    if missing_categories:
        errors.append("Missing categories: %s" % ", ".join(missing_categories))
    expected_classes = {item.value for item in FailureClass}
    if expected_classes - seen_classes:
        errors.append("Missing known failure classes: %s" % ", ".join(sorted(expected_classes - seen_classes)))
    rubric = Path(project_root) / "evaluation" / "RUBRIC.md"
    if not rubric.exists() or "frozen v1.0" not in rubric.read_text(encoding="utf-8"):
        errors.append("Evaluation rubric is missing or not frozen at v1.0")

    return {
        "valid": not errors,
        "case_count": len(definitions),
        "categories_present": sorted(seen_categories),
        "failure_classes_present": sorted(item for item in seen_classes if item),
        "synthetic_only": not any("possible endpoint" in item for item in errors),
        "fixture_hashes": fixture_hashes,
        "errors": errors,
    }

