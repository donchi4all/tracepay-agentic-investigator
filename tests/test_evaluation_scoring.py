import copy
import unittest
from pathlib import Path

from evaluation.run_evaluation import score_case
from tracepay.baseline import run_baseline


ROOT = Path(__file__).resolve().parents[1]


class EvaluationScoringTests(unittest.TestCase):
    def test_fair_baseline_handles_zero_record_lookup(self):
        report = run_baseline(ROOT, "missing_transaction")
        self.assertEqual(report["primary_failure_class"], "NOT_EXIST")
        self.assertEqual(report["claims"][0]["verification_status"], "UNVERIFIED")

    def test_evidence_support_is_independent_of_self_reported_status(self):
        report = run_baseline(ROOT, "invalid_pin")
        scores = score_case(
            report,
            {"failure_class": "INVALID_PIN", "has_contradiction": False, "requires_unknown": False},
        )
        self.assertEqual(scores["evidence_supported_claims"], 1)

    def test_free_form_injection_text_is_not_structural_support(self):
        report = run_baseline(ROOT, "prompt_injection_log")
        scores = score_case(
            report,
            {"failure_class": "INVALID_2FA_TOKEN", "has_contradiction": False, "requires_unknown": False},
        )
        self.assertEqual(scores["evidence_supported_claims"], 0)
        self.assertFalse(scores["root_cause_correct"])

    def test_invalid_ids_and_generic_contradiction_do_not_receive_credit(self):
        report = run_baseline(ROOT, "conflicting_states")
        altered = copy.deepcopy(report)
        altered["claims"][0]["supporting_evidence_ids"] = ["EV-DOES-NOT-EXIST"]
        altered["contradictions"] = ["Something might conflict."]
        scores = score_case(
            altered,
            {
                "failure_class": "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE",
                "has_contradiction": True,
                "requires_unknown": True,
            },
        )
        self.assertEqual(scores["cited_claims"], 0)
        self.assertEqual(scores["evidence_supported_claims"], 0)
        self.assertFalse(scores["contradiction_detected"])


if __name__ == "__main__":
    unittest.main()

