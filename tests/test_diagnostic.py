import unittest
from pathlib import Path

from tracepay.collector import EvidenceCollector
from tracepay.diagnostic import DiagnosticAgent
from tracepay.models import EvidenceItem
from tracepay.repository import FixtureRepository
from tracepay.trajectory import TrajectoryRecorder


ROOT = Path(__file__).resolve().parents[1]


class DiagnosticTests(unittest.TestCase):
    def diagnose_case(self, case_id):
        repository = FixtureRepository(ROOT)
        _, evidence, _ = EvidenceCollector(repository).collect(case_id, TrajectoryRecorder(None))
        return DiagnosticAgent().diagnose(evidence, TrajectoryRecorder(None))

    def test_empty_error_preserves_unknown(self):
        hypotheses, claims, contradictions, unknowns = self.diagnose_case("empty_error_context")
        self.assertEqual(hypotheses[0].failure_class.value, "EMPTY_OR_UNSTRUCTURED_ERROR")
        self.assertTrue(unknowns)
        self.assertFalse(contradictions)
        self.assertTrue(any(claim.classification.value == "UNKNOWN" for claim in claims))

    def test_missing_transaction_uses_search_evidence(self):
        hypotheses, claims, _, _ = self.diagnose_case("missing_transaction")
        self.assertEqual(hypotheses[0].failure_class.value, "NOT_EXIST")
        self.assertEqual(claims[0].supporting_evidence_ids, ["EV-missing_transaction-SEARCH"])

    def test_conflicting_states_are_not_forced_to_false_certainty(self):
        hypotheses, claims, contradictions, unknowns = self.diagnose_case("conflicting_states")
        self.assertEqual(
            hypotheses[0].failure_class.value, "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE"
        )
        self.assertLessEqual(hypotheses[0].confidence, 0.65)
        self.assertTrue(contradictions)
        self.assertTrue(unknowns)
        self.assertTrue(claims[0].contradicting_evidence_ids)

    def test_duplicate_events_remain_distinct_evidence(self):
        evidence = [
            EvidenceItem(
                evidence_id="EV-1",
                source_system="payment_service",
                record_id="one",
                transaction_reference="TX-SYN-DUP-EVENT",
                timestamp="2026-01-01T00:00:00Z",
                event_type="PAYMENT_STATE",
                sanitized_payload={"state": "FAILED", "reason_code": "INVALID_PIN"},
                integrity="sha256:test#1",
            ),
            EvidenceItem(
                evidence_id="EV-2",
                source_system="payment_service",
                record_id="two",
                transaction_reference="TX-SYN-DUP-EVENT",
                timestamp="2026-01-01T00:00:01Z",
                event_type="PAYMENT_STATE",
                sanitized_payload={"state": "FAILED", "reason_code": "INVALID_PIN"},
                integrity="sha256:test#2",
            ),
        ]
        hypotheses, claims, _, _ = DiagnosticAgent().diagnose(
            evidence, TrajectoryRecorder(None)
        )
        self.assertEqual(hypotheses[0].failure_class.value, "INVALID_PIN")
        self.assertEqual(claims[0].supporting_evidence_ids, ["EV-1", "EV-2"])


if __name__ == "__main__":
    unittest.main()

