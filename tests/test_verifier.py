import unittest

from tracepay.models import (
    ClaimClassification,
    DiagnosticClaim,
    EvidenceItem,
    VerificationStatus,
)
from tracepay.trajectory import TrajectoryRecorder
from tracepay.verifier import VerificationAgent


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.evidence = [
            EvidenceItem(
                evidence_id="EV-1",
                source_system="payment_service",
                record_id="one",
                transaction_reference="TX-SYN-VERIFY",
                timestamp="2026-01-01T00:00:00Z",
                event_type="PAYMENT_STATE",
                sanitized_payload={"state": "FAILED", "reason_code": "INVALID_PIN"},
                integrity="sha256:test",
            )
        ]

    def test_missing_citation_is_rejected(self):
        claim = DiagnosticClaim(
            claim_id="CLM-ROOT",
            statement="The transaction failed because authentication rejected an invalid PIN.",
            classification=ClaimClassification.INFERENCE,
            supporting_evidence_ids=["EV-MISSING"],
            contradicting_evidence_ids=[],
            confidence=0.9,
        )
        accepted, rejected = VerificationAgent().verify(
            [claim], self.evidence, TrajectoryRecorder(None)
        )
        self.assertEqual(accepted, [])
        self.assertEqual(rejected[0].verification_status, VerificationStatus.REJECTED)

    def test_semantically_unsupported_claim_is_rejected_even_with_valid_id(self):
        claim = DiagnosticClaim(
            claim_id="CLM-ROOT",
            statement="The request was rejected as a duplicate or previously processed request.",
            classification=ClaimClassification.INFERENCE,
            supporting_evidence_ids=["EV-1"],
            contradicting_evidence_ids=[],
            confidence=0.9,
        )
        accepted, rejected = VerificationAgent().verify(
            [claim], self.evidence, TrajectoryRecorder(None)
        )
        self.assertFalse(accepted)
        self.assertEqual(len(rejected), 1)


if __name__ == "__main__":
    unittest.main()

