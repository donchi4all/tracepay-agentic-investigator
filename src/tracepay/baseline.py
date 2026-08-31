"""Fair keyword-and-template baseline using the same sanitized evidence."""

import json
from pathlib import Path
from typing import Any, Dict, List

from .collector import EvidenceCollector
from .models import FailureClass
from .repository import FixtureRepository
from .trajectory import TrajectoryRecorder


# NO_ACTION_REQUIRED appears first. This is a normal fixed-rule choice and exposes
# the baseline's inability to distinguish structural codes from hostile log prose.
KEYWORDS = [
    FailureClass.NO_ACTION_REQUIRED,
    FailureClass.INVALID_PIN,
    FailureClass.INVALID_2FA_TOKEN,
    FailureClass.INVALID_CBA_RESPONSE_DATA,
    FailureClass.FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED,
    FailureClass.FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED,
    FailureClass.FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED,
    FailureClass.DUPLICATE_OR_ALREADY_PROCESSED_REQUEST,
    FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE,
]


def run_baseline(project_root: Path, case_id: str) -> Dict[str, Any]:
    repository = FixtureRepository(project_root)
    case, evidence, _ = EvidenceCollector(repository).collect(
        case_id, TrajectoryRecorder(None)
    )
    records = [item for item in evidence if item.event_type != "SEARCH_RESULT"]
    predicted = None
    matching_ids: List[str] = []
    # A zero-result check is a basic, gold-independent behavior expected of a
    # reasonable lookup baseline. The initial audited baseline omitted it.
    if not records:
        predicted = FailureClass.NOT_EXIST
        matching_ids = [item.evidence_id for item in evidence if item.event_type == "SEARCH_RESULT"]
    else:
        for candidate in KEYWORDS:
            needle = candidate.value
            if candidate == FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE:
                needle = "TIMEOUT"
            matches = [
                item.evidence_id
                for item in evidence
                if needle in json.dumps(item.sanitized_payload, sort_keys=True).upper()
            ]
            if matches:
                predicted = candidate
                matching_ids = matches
                break
    if predicted is None:
        predicted = FailureClass.EMPTY_OR_UNSTRUCTURED_ERROR
        matching_ids = [
            item.evidence_id
            for item in evidence
            if item.event_type == "SEARCH_RESULT"
            or str(item.sanitized_payload.get("state", "")).upper() in ("FAILED", "DENIED")
        ]
    unknowns = []
    if predicted in (
        FailureClass.EMPTY_OR_UNSTRUCTURED_ERROR,
        FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE,
    ):
        unknowns.append("The fixed keyword baseline cannot resolve the specific underlying state.")
    claim = {
        "claim_id": "BASE-ROOT",
        "statement": "Keyword/template diagnosis: %s." % predicted.value,
        "classification": "INFERENCE",
        "supporting_evidence_ids": matching_ids,
        "contradicting_evidence_ids": [],
        "confidence": 0.7 if matching_ids else 0.4,
        "verification_status": "UNVERIFIED",
    }
    return {
        "schema_version": "1.0-baseline",
        "case_id": case_id,
        "transaction_reference": case["transaction_reference"],
        "generated_at": next(
            item.timestamp for item in evidence if item.event_type == "SEARCH_RESULT"
        ),
        "primary_failure_class": predicted.value,
        "confidence": claim["confidence"],
        "executive_summary": claim["statement"],
        "impact": "Synthetic investigation only; impact is not assessed by the baseline.",
        "timeline": [item.to_dict() for item in sorted(evidence, key=lambda item: item.timestamp)],
        "hypotheses": [
            {
                "failure_class": predicted.value,
                "confidence": claim["confidence"],
                "rationale": "First matching keyword in a fixed ordered list.",
                "evidence_ids": matching_ids,
            }
        ],
        "claims": [claim],
        "rejected_claims": [],
        "contradictions": [],
        "unknowns": unknowns,
        "missing_sources": [],
        "recommendations": [
            {
                "action": "Have a payment operations engineer review the baseline output before any follow-up.",
                "approval": "REQUIRES_HUMAN_APPROVAL",
                "rationale": "The baseline is advisory and cannot change financial state.",
            }
        ],
        "safety_notice": "REQUIRES_HUMAN_APPROVAL: no financial action was executed.",
        "trajectory_path": "",
        "metadata": {
            "mode": "baseline",
            "provider": "deterministic_keyword",
            "financial_actions_executed": 0,
            "generated_at_basis": "latest_synthetic_evidence_or_dataset_freeze",
        },
    }
