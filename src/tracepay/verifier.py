"""Claim-level evidence verification and confidence calibration."""

from typing import List, Sequence, Tuple

from .models import DiagnosticClaim, EvidenceItem, VerificationStatus
from .trajectory import TrajectoryRecorder


def _structural_values(evidence: Sequence[EvidenceItem]) -> List[str]:
    values: List[str] = []
    for item in evidence:
        values.append(item.event_type.upper())
        for key in ("error_code", "reason_code", "rule_code", "state", "response_code"):
            values.append(str(item.sanitized_payload.get(key, "")).upper())
    return values


def _semantically_supported(claim: DiagnosticClaim, evidence: Sequence[EvidenceItem]) -> bool:
    """Check report semantics against allow-listed structural evidence, not log prose."""
    if claim.claim_id.startswith("CLM-UNKNOWN"):
        return True
    values = _structural_values(evidence)
    joined = " ".join(values)
    statement = claim.statement.lower()
    expected_by_phrase = {
        "invalid pin": "INVALID_PIN",
        "second-factor token": "INVALID_2FA_TOKEN",
        "initiator count": "FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED",
        "initiator amount": "FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED",
        "approver amount": "FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED",
        "response contract": "INVALID_CBA_RESPONSE_DATA",
        "duplicate or previously processed": "DUPLICATE_OR_ALREADY_PROCESSED_REQUEST",
    }
    for phrase, structural_code in expected_by_phrase.items():
        if phrase in statement:
            return structural_code in joined
    if "no transaction record exists" in statement:
        return any(
            item.event_type == "SEARCH_RESULT"
            and item.sanitized_payload.get("matched_records") == 0
            for item in evidence
        )
    if "completed/posted" in statement:
        return "COMPLETED" in values and "POSTED" in values
    if "no structured error code" in statement:
        return any(item.sanitized_payload.get("error") == {} for item in evidence)
    if "timeout or otherwise unknown downstream state" in statement:
        return (
            "DOWNSTREAM_TIMEOUT" in values
            or "DOWNSTREAM_TIMEOUT" in joined
            or ("FAILED" in values and "POSTED" in values)
        )
    if "conflicts with mock cba" in statement:
        return "FAILED" in values and "POSTED" in values
    return False


class VerificationAgent:
    def verify(
        self,
        claims: Sequence[DiagnosticClaim],
        evidence: Sequence[EvidenceItem],
        recorder: TrajectoryRecorder,
    ) -> Tuple[List[DiagnosticClaim], List[DiagnosticClaim]]:
        recorder.record(
            "verification_agent",
            "instruction",
            "Verify every material claim against collected evidence and calibrate confidence.",
            "Unsupported claims cannot reach the report as accepted conclusions.",
            {"claim_count": len(claims)},
        )
        known_ids = {item.evidence_id for item in evidence}
        accepted: List[DiagnosticClaim] = []
        rejected: List[DiagnosticClaim] = []

        for claim in claims:
            input_confidence = claim.confidence
            support_valid = bool(claim.supporting_evidence_ids) and all(
                item_id in known_ids for item_id in claim.supporting_evidence_ids
            )
            contradict_valid = all(item_id in known_ids for item_id in claim.contradicting_evidence_ids)
            semantic_valid = _semantically_supported(claim, evidence)
            if not support_valid or not contradict_valid or not semantic_valid:
                claim.verification_status = VerificationStatus.REJECTED
                claim.confidence = 0.0
                rejected.append(claim)
                recorder.record(
                    "verification_agent",
                    "verification_feedback",
                    "Reject an unsupported material claim.",
                    "A citation is missing/invalid or allow-listed structural fields do not support the statement.",
                    {
                        "claim_id": claim.claim_id,
                        "input_confidence": input_confidence,
                        "output_confidence": claim.confidence,
                        "semantic_valid": semantic_valid,
                        "status": claim.verification_status.value,
                    },
                )
                continue
            if claim.contradicting_evidence_ids:
                claim.verification_status = VerificationStatus.CONFLICTED
                claim.confidence = min(claim.confidence, 0.65)
            else:
                claim.verification_status = VerificationStatus.VERIFIED
            accepted.append(claim)
            recorder.record(
                "verification_agent",
                "verification_feedback",
                "Accept a structurally supported material claim.",
                "The cited evidence IDs exist and allow-listed structural fields support the statement.",
                {
                    "claim_id": claim.claim_id,
                    "input_confidence": input_confidence,
                    "output_confidence": claim.confidence,
                    "semantic_valid": semantic_valid,
                    "status": claim.verification_status.value,
                },
            )

        recorder.record(
            "verification_agent",
            "tool_response",
            "Return accepted and rejected claim sets.",
            "Verification status and confidence are explicit in the report contract.",
            {"accepted": len(accepted), "rejected": len(rejected)},
        )
        return accepted, rejected
