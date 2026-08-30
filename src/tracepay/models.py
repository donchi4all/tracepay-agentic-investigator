"""Typed contracts shared by all TracePay components."""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class FailureClass(str, Enum):
    INVALID_PIN = "INVALID_PIN"
    NOT_EXIST = "NOT_EXIST"
    NO_ACTION_REQUIRED = "NO_ACTION_REQUIRED"
    INVALID_2FA_TOKEN = "INVALID_2FA_TOKEN"
    INVALID_CBA_RESPONSE_DATA = "INVALID_CBA_RESPONSE_DATA"
    FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED = "FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED"
    FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED = "FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED"
    FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED = "FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED"
    EMPTY_OR_UNSTRUCTURED_ERROR = "EMPTY_OR_UNSTRUCTURED_ERROR"
    TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE = "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE"
    DUPLICATE_OR_ALREADY_PROCESSED_REQUEST = "DUPLICATE_OR_ALREADY_PROCESSED_REQUEST"


class ClaimClassification(str, Enum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    UNKNOWN = "UNKNOWN"


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    CONFLICTED = "CONFLICTED"
    REJECTED = "REJECTED"
    UNVERIFIED = "UNVERIFIED"


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    return value


@dataclass
class EvidenceItem:
    evidence_id: str
    source_system: str
    record_id: str
    transaction_reference: str
    timestamp: str
    event_type: str
    sanitized_payload: Dict[str, Any]
    integrity: str

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class DiagnosticClaim:
    claim_id: str
    statement: str
    classification: ClaimClassification
    supporting_evidence_ids: List[str]
    contradicting_evidence_ids: List[str]
    confidence: float
    verification_status: VerificationStatus = VerificationStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class Hypothesis:
    failure_class: FailureClass
    confidence: float
    rationale: str
    evidence_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class Recommendation:
    action: str
    approval: str = "REQUIRES_HUMAN_APPROVAL"
    rationale: str = "TracePay is advisory and cannot change financial state."

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class InvestigationReport:
    schema_version: str
    case_id: str
    transaction_reference: str
    generated_at: str
    primary_failure_class: FailureClass
    confidence: float
    executive_summary: str
    impact: str
    timeline: List[Dict[str, Any]]
    hypotheses: List[Hypothesis]
    claims: List[DiagnosticClaim]
    rejected_claims: List[DiagnosticClaim]
    contradictions: List[str]
    unknowns: List[str]
    missing_sources: List[str]
    recommendations: List[Recommendation]
    safety_notice: str
    trajectory_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))

