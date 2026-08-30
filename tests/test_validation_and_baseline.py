import unittest
from pathlib import Path

from tracepay.baseline import run_baseline
from tracepay.repository import FixtureRepository
from tracepay.validation import validate_dataset


ROOT = Path(__file__).resolve().parents[1]


class ValidationAndBaselineTests(unittest.TestCase):
    def test_dataset_is_frozen_diverse_and_synthetic(self):
        result = validate_dataset(ROOT)
        self.assertTrue(result["valid"], result["errors"])
        self.assertGreaterEqual(result["case_count"], 12)
        self.assertTrue(result["synthetic_only"])

    def test_gold_labels_are_not_present_in_baseline_input(self):
        repository = FixtureRepository(ROOT)
        for definition in repository.case_definitions():
            fixture = repository.load_case(definition["case_id"])
            self.assertNotIn("gold", fixture)

    def test_baseline_is_functional_and_safe(self):
        report = run_baseline(ROOT, "invalid_pin")
        self.assertEqual(report["primary_failure_class"], "INVALID_PIN")
        self.assertTrue(report["claims"][0]["supporting_evidence_ids"])
        self.assertEqual(
            report["recommendations"][0]["approval"], "REQUIRES_HUMAN_APPROVAL"
        )
        self.assertEqual(report["metadata"]["financial_actions_executed"], 0)


if __name__ == "__main__":
    unittest.main()

