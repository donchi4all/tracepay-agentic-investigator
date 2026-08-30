"""Controlled end-to-end investigation orchestration."""

from copy import deepcopy
from pathlib import Path
from typing import List, Optional, Tuple

from .collector import EvidenceCollector
from .diagnostic import DiagnosticAgent
from .models import (
    ClaimClassification,
    DiagnosticClaim,
    InvestigationReport,
    Recommendation,
    VerificationStatus,
)
from .reporting import ReportGenerator
from .repository import FixtureRepository
from .trajectory import TrajectoryRecorder
from .verifier import VerificationAgent


EXPECTED_SOURCES = ["payment_service", "auth_service", "approval_workflow", "mock_cba"]
VALID_MODES = ("stage1", "stage2", "stage3", "stage4_removed", "final")


def _privacy_safe_path(path: Optional[Path], project_root: Path) -> str:
    if not path:
        return ""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(project_root).as_posix()
    except ValueError:
        # Temporary/external destinations must not expose a user's home path.
        return resolved.name


class Coordinator:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.repository = FixtureRepository(self.project_root)
        self.collector = EvidenceCollector(self.repository)
        self.diagnostic = DiagnosticAgent()
        self.verifier = VerificationAgent()
        self.reporter = ReportGenerator()

    def investigate(
        self,
        case_id: str,
        mode: str = "final",
        output_dir: Optional[Path] = None,
        trajectory_path: Optional[Path] = None,
    ) -> Tuple[InvestigationReport, Optional[Path], Optional[Path]]:
        if mode not in VALID_MODES:
            raise ValueError("Unsupported mode: %s" % mode)
        recorder = TrajectoryRecorder(trajectory_path)
        recorder.record(
            "coordinator",
            "instruction",
            "Investigate one synthetic transaction using the fixed component sequence.",
            "Controlled orchestration keeps the evidence and safety boundaries observable.",
            {"case_id": case_id, "mode": mode},
        )
        plan = ["collect", "reconcile", "verify", "report"]
        recorder.record(
            "coordinator",
            "plan",
            "Create the investigation plan.",
            "Each downstream component has one bounded responsibility.",
            {"steps": plan},
        )

        case, evidence, security_findings = self.collector.collect(case_id, recorder)
        hypotheses, raw_claims, contradictions, unknowns = self.diagnostic.diagnose(
            evidence, recorder
        )
        claims = deepcopy(raw_claims)
        rejected: List[DiagnosticClaim] = []

        if mode == "stage1":
            for claim in claims:
                claim.supporting_evidence_ids = []
                claim.contradicting_evidence_ids = []
                claim.verification_status = VerificationStatus.UNVERIFIED
            recorder.record(
                "coordinator",
                "experiment_boundary",
                "Stop after correlation and prose-style diagnosis.",
                "Stage 1 intentionally measures correlation before structured citations.",
                {},
            )
            contradictions = []
        elif mode == "stage2":
            for claim in claims:
                claim.verification_status = VerificationStatus.UNVERIFIED
            recorder.record(
                "coordinator",
                "experiment_boundary",
                "Preserve structured claims and citations without verification.",
                "Stage 2 isolates the value of the evidence contract.",
                {},
            )
            contradictions = []
        else:
            claims, rejected = self.verifier.verify(claims, evidence, recorder)

        if mode == "stage4_removed":
            # This intentionally recorded experiment represents unconstrained fan-out.
            # It is never used by final mode and is visibly marked unverified.
            alternatives = [
                "A network issue may have caused the failure.",
                "A customer input issue may have caused the failure.",
                "A downstream maintenance event may have caused the failure.",
            ]
            for index, statement in enumerate(alternatives, 1):
                claims.append(
                    DiagnosticClaim(
                        claim_id="CLM-FANOUT-%d" % index,
                        statement=statement,
                        classification=ClaimClassification.INFERENCE,
                        supporting_evidence_ids=[],
                        contradicting_evidence_ids=[],
                        confidence=0.2,
                        verification_status=VerificationStatus.UNVERIFIED,
                    )
                )
            recorder.record(
                "coordinator",
                "experiment",
                "Append unconstrained alternative hypotheses after verification.",
                "Stage 4 measures whether speculative fan-out adds useful coverage or only unsupported claims.",
                {"added_claims": len(alternatives), "candidate_for_removal": True},
            )

        root_claim = next((claim for claim in claims if claim.claim_id == "CLM-ROOT"), raw_claims[0])
        source_systems = {item.source_system for item in evidence}
        missing_sources = [item for item in EXPECTED_SOURCES if item not in source_systems]
        primary = hypotheses[0].failure_class
        confidence = root_claim.confidence
        summary = "%s %s" % (
            root_claim.statement,
            (
                "Conflicting component state requires reconciliation before any operational decision."
                if contradictions
                else "The conclusion is limited to the cited synthetic evidence."
            ),
        )
        recommendations = [
            Recommendation(
                action="Have a payment operations engineer review the cited evidence before any operational follow-up."
            )
        ]
        if primary.value == "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE":
            recommendations.append(
                Recommendation(
                    action="Obtain a read-only downstream reconciliation result; do not retry or reverse from this report."
                )
            )
        elif primary.value == "NO_ACTION_REQUIRED":
            recommendations.append(
                Recommendation(
                    action="Confirm the consistent final state; do not create a duplicate retry from this report."
                )
            )
        else:
            recommendations.append(
                Recommendation(
                    action="Route the diagnosed class to the owning support team; any payment-state action requires separate review."
                )
            )

        report = InvestigationReport(
            schema_version="1.0",
            case_id=case_id,
            transaction_reference=case["transaction_reference"],
            generated_at="2026-08-29T00:00:00Z",
            primary_failure_class=primary,
            confidence=confidence,
            executive_summary=summary,
            impact="Synthetic investigation only. No real customer, account, or financial impact is asserted.",
            timeline=[item.to_dict() for item in sorted(evidence, key=lambda item: item.timestamp)],
            hypotheses=hypotheses,
            claims=claims,
            rejected_claims=rejected,
            contradictions=contradictions,
            unknowns=unknowns,
            missing_sources=missing_sources,
            recommendations=recommendations,
            safety_notice=(
                "REQUIRES_HUMAN_APPROVAL: TracePay is read-only. It did not and cannot execute a payment, "
                "retry, reversal, block, approval, customer contact, or state change."
            ),
            trajectory_path=_privacy_safe_path(trajectory_path, self.project_root),
            metadata={
                "mode": mode,
                "provider": "deterministic_local",
                "security_findings": security_findings,
                "financial_actions_executed": 0,
            },
        )
        markdown_path: Optional[Path] = None
        json_path: Optional[Path] = None
        if output_dir:
            markdown_path, json_path = self.reporter.write(report, output_dir, recorder)
        else:
            recorder.record(
                "report_generator",
                "tool_response",
                "Return the report object without filesystem output.",
                "Evaluation consumes the same report contract in memory.",
                {"case_id": case_id},
            )
        recorder.record(
            "coordinator",
            "complete",
            "Close the investigation in advisory mode.",
            "All material final claims passed through the configured stage boundary.",
            {"primary_failure_class": primary.value, "financial_actions_executed": 0},
        )
        return report, markdown_path, json_path
