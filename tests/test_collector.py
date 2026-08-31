import json
import tempfile
import unittest
from pathlib import Path

from tracepay.collector import EvidenceCollector
from tracepay.repository import FixtureRepository
from tracepay.trajectory import TrajectoryRecorder


ROOT = Path(__file__).resolve().parents[1]


class FakeRepository:
    def load_case(self, case_id):
        return {
            "case_id": case_id,
            "transaction_reference": "TX-SYN-MALFORMED",
            "records": [
                {
                    "source_system": "application_log",
                    "record_id": "broken-1",
                    "timestamp": "bad",
                    "event_type": "LOG_MESSAGE",
                    "payload": {"state": "FAILED"},
                }
            ],
        }

    def integrity(self, case_id):
        return "sha256:synthetic"

    def dataset_frozen_at(self):
        return "2026-08-29T00:00:00Z"


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.repository = FixtureRepository(ROOT)

    def test_evidence_contract_and_fixture_are_read_only(self):
        path = self.repository.fixture_path("invalid_pin")
        before = path.read_bytes()
        _, evidence, _ = EvidenceCollector(self.repository).collect(
            "invalid_pin", TrajectoryRecorder(None)
        )
        after = path.read_bytes()
        self.assertEqual(before, after)
        required = {
            "evidence_id",
            "source_system",
            "record_id",
            "transaction_reference",
            "timestamp",
            "event_type",
            "sanitized_payload",
            "integrity",
        }
        self.assertTrue(all(required == set(item.to_dict()) for item in evidence))
        auth = next(item for item in evidence if item.source_system == "auth_service")
        self.assertEqual(auth.sanitized_payload["pin"], "[REDACTED]")
        self.assertEqual(auth.sanitized_payload["token"], "[REDACTED]")

    def test_malformed_timestamp_uses_explicit_fallback_and_records_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trajectory.jsonl"
            _, evidence, _ = EvidenceCollector(self.repository).collect(
                "invalid_cba_response", TrajectoryRecorder(path)
            )
            cba = next(item for item in evidence if item.record_id == "cba-bad-1")
            self.assertEqual(cba.timestamp, "2026-08-20T12:00:04Z")
            events = [json.loads(line)["event"] for line in path.read_text().splitlines()]
            self.assertIn("validation_feedback", events)
            self.assertIn("retry_success", events)

    def test_malformed_record_without_fallback_is_skipped_not_invented(self):
        _, evidence, _ = EvidenceCollector(FakeRepository()).collect(
            "malformed", TrajectoryRecorder(None)
        )
        self.assertEqual([item.event_type for item in evidence], ["SEARCH_RESULT"])
        self.assertEqual(evidence[0].sanitized_payload["matched_records"], 0)

    def test_hostile_log_is_flagged(self):
        _, evidence, findings = EvidenceCollector(self.repository).collect(
            "prompt_injection_log", TrajectoryRecorder(None)
        )
        self.assertEqual(len(findings), 1)
        self.assertTrue(any(item.source_system == "application_log" for item in evidence))


if __name__ == "__main__":
    unittest.main()
