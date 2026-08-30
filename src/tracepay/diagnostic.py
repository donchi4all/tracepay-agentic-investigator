"""Deterministic state reconciliation and ranked diagnosis."""

from typing import Any, Dict, List, Sequence, Tuple

from .models import (
    ClaimClassification,
    DiagnosticClaim,
    EvidenceItem,
    FailureClass,
    Hypothesis,
)
from .trajectory import TrajectoryRecorder


STRUCTURAL_CODE_FIELDS = ("error_code", "reason_code", "rule_code")


def _records(evidence: Sequence[EvidenceItem]) -> List[EvidenceItem]:
    return [item for item in evidence if item.event_type != "SEARCH_RESULT"]


def _field_matches(
    evidence: Sequence[EvidenceItem], fields: Sequence[str], expected: str
) -> List[str]:
    return [
        item.evidence_id
        for item in _records(evidence)
        if any(str(item.sanitized_payload.get(field, "")).upper() == expected for field in fields)
    ]


def _state_ids(evidence: Sequence[EvidenceItem], source: str, state: str) -> List[str]:
    return [
        item.evidence_id
        for item in _records(evidence)
        if item.source_system == source
        and str(item.sanitized_payload.get("state", "")).upper() == state
    ]


def _statement(failure_class: FailureClass) -> str:
    descriptions = {
        FailureClass.INVALID_PIN: "The transaction failed because authentication rejected an invalid PIN.",
        FailureClass.INVALID_2FA_TOKEN: "The transaction failed because authentication rejected the second-factor token.",
        FailureClass.FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED: "The transaction was rejected by the first-time initiator count limit.",
        FailureClass.FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED: "The transaction was rejected by the first-time initiator amount limit.",
        FailureClass.FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED: "The transaction was rejected by the first-time approver amount limit.",
        FailureClass.INVALID_CBA_RESPONSE_DATA: "The transaction failed because the mock CBA response did not satisfy the response contract.",
        FailureClass.NOT_EXIST: "No transaction record exists for the supplied reference in any synthetic source.",
        FailureClass.NO_ACTION_REQUIRED: "The transaction is already in a consistent completed/posted state; no payment-state action is indicated.",
        FailureClass.EMPTY_OR_UNSTRUCTURED_ERROR: "The available failure contains no structured error code, so the specific technical cause is unresolved.",
        FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE: "The most likely class is a timeout or otherwise unknown downstream state.",
        FailureClass.DUPLICATE_OR_ALREADY_PROCESSED_REQUEST: "The request was rejected as a duplicate or previously processed request.",
    }
    return descriptions[failure_class]


class DiagnosticAgent:
    def diagnose(
        self, evidence: List[EvidenceItem], recorder: TrajectoryRecorder
    ) -> Tuple[List[Hypothesis], List[DiagnosticClaim], List[str], List[str]]:
        recorder.record(
            "state_reconciler",
            "instruction",
            "Build a timeline, compare component states, and rank evidence-backed hypotheses.",
            "Only allow-listed structural fields are diagnostic inputs; free-form log messages are untrusted data.",
            {},
        )
        records = _records(evidence)
        search_id = [item.evidence_id for item in evidence if item.event_type == "SEARCH_RESULT"]
        contradictions: List[str] = []
        unknowns: List[str] = []

        failed_ids = _state_ids(evidence, "payment_service", "FAILED")
        posted_ids = _state_ids(evidence, "mock_cba", "POSTED")
        has_state_conflict = bool(failed_ids and posted_ids)

        if not records:
            primary = FailureClass.NOT_EXIST
            support_ids = search_id
            confidence = 0.99
        elif has_state_conflict:
            primary = FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE
            support_ids = failed_ids + posted_ids
            confidence = 0.62
            contradictions.append("Payment service state FAILED conflicts with mock CBA state POSTED.")
            unknowns.append("The authoritative downstream outcome and any required operational response remain unknown.")
        else:
            primary = None  # type: ignore
            support_ids = []
            confidence = 0.0
            for candidate in FailureClass:
                if candidate in (
                    FailureClass.NOT_EXIST,
                    FailureClass.NO_ACTION_REQUIRED,
                    FailureClass.EMPTY_OR_UNSTRUCTURED_ERROR,
                    FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE,
                ):
                    continue
                matches = _field_matches(evidence, STRUCTURAL_CODE_FIELDS, candidate.value)
                if matches:
                    primary = candidate
                    support_ids = matches
                    confidence = 0.98 if len(matches) > 1 else 0.92
                    break

            completed_ids = _state_ids(evidence, "payment_service", "COMPLETED")
            if primary is None and completed_ids and posted_ids:
                primary = FailureClass.NO_ACTION_REQUIRED
                support_ids = completed_ids + posted_ids
                confidence = 0.98

            timeout_ids = [
                item.evidence_id
                for item in records
                if item.event_type == "DOWNSTREAM_TIMEOUT"
                or "TIMEOUT" in str(item.sanitized_payload.get("reason_code", "")).upper()
            ]
            if primary is None and timeout_ids:
                primary = FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE
                support_ids = timeout_ids
                confidence = 0.72
                unknowns.append("No final mock CBA response is present, so downstream financial state is unknown.")

            if primary is None:
                empty_ids = [
                    item.evidence_id
                    for item in records
                    if item.sanitized_payload.get("error") == {}
                    or str(item.sanitized_payload.get("state", "")).upper() in ("FAILED", "DENIED")
                ]
                primary = FailureClass.EMPTY_OR_UNSTRUCTURED_ERROR
                support_ids = empty_ids or [records[-1].evidence_id]
                confidence = 0.78
                unknowns.append("The specific technical cause cannot be determined from the available structured fields.")

        assert primary is not None
        hypotheses = [
            Hypothesis(
                failure_class=primary,
                confidence=confidence,
                rationale="Selected from correlated structural states and allow-listed failure-code fields.",
                evidence_ids=list(dict.fromkeys(support_ids)),
            )
        ]
        if primary == FailureClass.TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE:
            hypotheses.append(
                Hypothesis(
                    failure_class=FailureClass.EMPTY_OR_UNSTRUCTURED_ERROR,
                    confidence=0.25,
                    rationale="Incomplete downstream evidence leaves a lower-ranked generic unknown-error alternative.",
                    evidence_ids=list(dict.fromkeys(support_ids)),
                )
            )

        claims = [
            DiagnosticClaim(
                claim_id="CLM-ROOT",
                statement=_statement(primary),
                classification=ClaimClassification.INFERENCE,
                supporting_evidence_ids=list(dict.fromkeys(support_ids)),
                contradicting_evidence_ids=(failed_ids + posted_ids) if has_state_conflict else [],
                confidence=confidence,
            )
        ]
        if has_state_conflict:
            claims.append(
                DiagnosticClaim(
                    claim_id="CLM-CONFLICT",
                    statement=contradictions[0],
                    classification=ClaimClassification.FACT,
                    supporting_evidence_ids=failed_ids + posted_ids,
                    contradicting_evidence_ids=failed_ids + posted_ids,
                    confidence=1.0,
                )
            )
        for index, unknown in enumerate(unknowns, 1):
            claims.append(
                DiagnosticClaim(
                    claim_id="CLM-UNKNOWN-%d" % index,
                    statement=unknown,
                    classification=ClaimClassification.UNKNOWN,
                    supporting_evidence_ids=list(dict.fromkeys(support_ids)),
                    contradicting_evidence_ids=[],
                    confidence=min(confidence, 0.65),
                )
            )

        recorder.record(
            "state_reconciler",
            "tool_response",
            "Return ranked hypotheses and structured diagnostic claims.",
            "The top hypothesis follows explicit evidence priority and preserves uncertainty on ambiguous cases.",
            {
                "primary_failure_class": primary.value,
                "confidence": confidence,
                "claim_count": len(claims),
                "contradiction_count": len(contradictions),
            },
        )
        return hypotheses, claims, contradictions, unknowns

