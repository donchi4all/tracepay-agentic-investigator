import json
import tempfile
import unittest
from pathlib import Path

from tracepay.coordinator import Coordinator
from tracepay.reporting import render_markdown
from tracepay.repository import FixtureRepository


ROOT = Path(__file__).resolve().parents[1]


class EndToEndTests(unittest.TestCase):
    def test_all_gold_classes_and_claim_contracts(self):
        repository = FixtureRepository(ROOT)
        coordinator = Coordinator(ROOT)
        for definition in repository.case_definitions():
            with self.subTest(case=definition["case_id"]):
                report = coordinator.investigate(definition["case_id"])[0]
                self.assertEqual(
                    report.primary_failure_class.value,
                    definition["gold"]["failure_class"],
                )
                evidence_ids = {item["evidence_id"] for item in report.timeline}
                self.assertTrue(report.claims)
                for claim in report.claims:
                    self.assertIn(claim.verification_status.value, ("VERIFIED", "CONFLICTED"))
                    self.assertTrue(claim.supporting_evidence_ids)
                    self.assertTrue(set(claim.supporting_evidence_ids) <= evidence_ids)
                self.assertTrue(
                    all(item.approval == "REQUIRES_HUMAN_APPROVAL" for item in report.recommendations)
                )
                self.assertEqual(report.metadata["financial_actions_executed"], 0)

    def test_prompt_injection_cannot_override_structural_auth_code(self):
        report = Coordinator(ROOT).investigate("prompt_injection_log")[0]
        self.assertEqual(report.primary_failure_class.value, "INVALID_2FA_TOKEN")
        self.assertTrue(report.metadata["security_findings"])

    def test_report_writes_markdown_json_and_observable_agents(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            trajectory = base / "trajectory.jsonl"
            report, markdown, json_path = Coordinator(ROOT).investigate(
                "conflicting_states",
                output_dir=base,
                trajectory_path=trajectory,
            )
            self.assertTrue(markdown.exists())
            self.assertTrue(json_path.exists())
            parsed = json.loads(json_path.read_text())
            self.assertEqual(parsed["primary_failure_class"], report.primary_failure_class.value)
            self.assertIn("REQUIRES_HUMAN_APPROVAL", markdown.read_text())
            events = [json.loads(line) for line in trajectory.read_text().splitlines()]
            agents = {item["agent"] for item in events}
            self.assertEqual(
                agents,
                {
                    "coordinator",
                    "evidence_collector",
                    "state_reconciler",
                    "verification_agent",
                    "report_generator",
                },
            )
            self.assertTrue(any(item["event"] == "human_checkpoint" for item in events))
            self.assertTrue(any(item["event"] == "verification_feedback" for item in events))
            self.assertTrue(
                any(
                    item["event"] == "verification_feedback"
                    and item["details"].get("status") == "CONFLICTED"
                    and item["details"].get("output_confidence", 1.0)
                    < item["details"].get("input_confidence", 0.0)
                    for item in events
                )
            )

    def test_timeline_is_sorted_despite_conflicting_source_order(self):
        report = Coordinator(ROOT).investigate("conflicting_states")[0]
        timestamps = [item["timestamp"] for item in report.timeline]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_reports_regenerate_deterministically_from_evidence_snapshot(self):
        first = Coordinator(ROOT).investigate("invalid_pin")[0]
        second = Coordinator(ROOT).investigate("invalid_pin")[0]
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(render_markdown(first), render_markdown(second))
        self.assertEqual(first.generated_at, "2026-08-20T10:00:03Z")
        self.assertEqual(
            first.metadata["generated_at_basis"],
            "latest_synthetic_evidence_or_dataset_freeze",
        )

        missing = Coordinator(ROOT).investigate("missing_transaction")[0]
        self.assertEqual(missing.generated_at, "2026-08-29T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
