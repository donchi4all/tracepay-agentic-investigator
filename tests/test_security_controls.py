import ast
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from tracepay.collector import EvidenceCollector
from tracepay.coordinator import Coordinator
from tracepay.repository import FixtureRepository
from tracepay.safety import redact
from tracepay.trajectory import TrajectoryRecorder


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DATA = re.compile(
    r"https?://|\bprod(?:uction)?[._-]|BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY|"
    r"AKIA[0-9A-Z]{16}|\bsk-[A-Za-z0-9]{16,}|\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.",
    re.IGNORECASE,
)
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
LONG_DIGITS = re.compile(r"(?<![A-Za-z0-9])\d{8,19}(?![A-Za-z0-9])")
SENSITIVE_KEYS = re.compile(
    r"(^|_)(pin|otp|token|secret|password|account_?number|pan|api_?key)(_|$)",
    re.IGNORECASE,
)


class SecurityControlTests(unittest.TestCase):
    def setUp(self):
        self.repository = FixtureRepository(ROOT)
        self.definitions = self.repository.case_definitions()

    def test_01_fixtures_are_explicitly_synthetic_and_have_no_customer_or_production_data(self):
        for definition in self.definitions:
            with self.subTest(case=definition["case_id"]):
                fixture = self.repository.load_case(definition["case_id"])
                raw = json.dumps(fixture, sort_keys=True)
                self.assertTrue(fixture["transaction_reference"].startswith("TX-SYN-"))
                self.assertIsNone(FORBIDDEN_DATA.search(raw))
                self.assertIsNone(EMAIL.search(raw))
                self.assertIsNone(LONG_DIGITS.search(raw))
                self.assertNotIn("customer_name", raw.lower())
                self.assertNotIn("customer_id", raw.lower())
                self.assertNotIn("phone_number", raw.lower())

    def test_02_sensitive_fixture_fields_are_non_secret_sentinels_and_no_accounts_exist(self):
        found_sensitive_sentinels = 0
        for definition in self.definitions:
            fixture = self.repository.load_case(definition["case_id"])
            for record in fixture.get("records", []):
                for key, value in record.get("payload", {}).items():
                    if SENSITIVE_KEYS.search(key):
                        found_sensitive_sentinels += 1
                        self.assertRegex(str(value), r"^SYNTHETIC_[A-Z_]+_SENTINEL$")
                        self.assertFalse(str(value).isdigit())
                    self.assertNotIn("account_number", key.lower())
                    self.assertNotEqual(key.lower(), "pan")
        self.assertGreater(found_sensitive_sentinels, 0, "Expected sentinels to exercise redaction")

    def test_03_prompt_injection_log_cannot_control_final_diagnosis_or_citations(self):
        report = Coordinator(ROOT).investigate("prompt_injection_log")[0]
        self.assertEqual(report.primary_failure_class.value, "INVALID_2FA_TOKEN")
        self.assertTrue(report.metadata["security_findings"])
        root_claim = next(claim for claim in report.claims if claim.claim_id == "CLM-ROOT")
        self.assertNotIn("EV-prompt_injection_log-002", root_claim.supporting_evidence_ids)
        self.assertIn("EV-prompt_injection_log-003", root_claim.supporting_evidence_ids)

    def test_04_fixture_adapter_is_read_only_for_every_case(self):
        paths = [self.repository.fixture_path(item["case_id"]) for item in self.definitions]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for definition in self.definitions:
                Coordinator(ROOT).investigate(
                    definition["case_id"],
                    output_dir=base / "reports",
                    trajectory_path=base / (definition["case_id"] + ".jsonl"),
                )
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)
        public_methods = {
            name
            for name in dir(FixtureRepository)
            if not name.startswith("_") and callable(getattr(FixtureRepository, name))
        }
        self.assertEqual(
            public_methods,
            {"case_definition", "case_definitions", "fixture_path", "integrity", "load_case"},
        )

    def test_05_runtime_has_no_external_or_financial_mutation_capability(self):
        forbidden_imports = {"requests", "httpx", "socket", "subprocess", "urllib", "boto3"}
        forbidden_call_names = {
            "execute_payment", "retry_payment", "reverse_payment", "approve_payment",
            "block_account", "change_transaction_state",
        }
        for path in (ROOT / "src" / "tracepay").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imported = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names
            }
            called = {
                node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
            }
            self.assertFalse(imported & forbidden_imports, path)
            self.assertFalse(called & forbidden_call_names, path)
        for definition in self.definitions:
            report = Coordinator(ROOT).investigate(definition["case_id"])[0]
            self.assertEqual(report.metadata["financial_actions_executed"], 0)

    def test_06_sensitive_values_are_redacted_before_evidence_and_reports(self):
        raw_values = {
            "pin": "SYNTHETIC_PIN_SENTINEL",
            "otp": "SYNTHETIC_OTP_SENTINEL",
            "token": "SYNTHETIC_TOKEN_SENTINEL",
            "account_number": "9" * 12,
        }
        sanitized = redact(raw_values)
        self.assertTrue(all(value == "[REDACTED]" for value in sanitized.values()))
        _, evidence, _ = EvidenceCollector(self.repository).collect(
            "invalid_pin", TrajectoryRecorder(None)
        )
        serialized = json.dumps([item.to_dict() for item in evidence])
        self.assertNotIn("SYNTHETIC_PIN_SENTINEL", serialized)
        self.assertNotIn("SYNTHETIC_TOKEN_SENTINEL", serialized)
        self.assertIn("[REDACTED]", serialized)

    def test_07_ambiguous_downstream_state_is_not_forced_to_failed_or_successful(self):
        for case_id in ("timeout_ambiguous", "conflicting_states"):
            with self.subTest(case=case_id):
                report = Coordinator(ROOT).investigate(case_id)[0]
                self.assertEqual(
                    report.primary_failure_class.value, "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE"
                )
                self.assertTrue(report.unknowns)
                self.assertIn("unknown", report.executive_summary.lower())
                self.assertNotIn("the transaction succeeded", report.executive_summary.lower())
                self.assertNotIn("the transaction failed.", report.executive_summary.lower())
        conflict = Coordinator(ROOT).investigate("conflicting_states")[0]
        self.assertLessEqual(conflict.confidence, 0.65)
        self.assertTrue(conflict.contradictions)

    def test_08_every_consequential_recommendation_requires_human_approval(self):
        for definition in self.definitions:
            report = Coordinator(ROOT).investigate(definition["case_id"])[0]
            self.assertTrue(report.recommendations)
            for recommendation in report.recommendations:
                self.assertEqual(recommendation.approval, "REQUIRES_HUMAN_APPROVAL")
            self.assertIn("REQUIRES_HUMAN_APPROVAL", report.safety_notice)

    def test_09_dependencies_and_licences_are_declared(self):
        project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        licence = (ROOT / "LICENSE").read_text(encoding="utf-8")
        security = (ROOT / "docs" / "SECURITY_AND_ETHICS.md").read_text(encoding="utf-8")
        self.assertIn('requires = ["setuptools==68.2.2"]', project)
        self.assertIn("dependencies = []", project)
        self.assertIn("MIT License", licence)
        self.assertIn("Python Software Foundation License", security)
        self.assertIn("setuptools", security)

    def test_10_trajectories_redact_secrets_pii_log_text_and_local_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            trajectory = base / "trace.jsonl"
            recorder = TrajectoryRecorder(trajectory)
            recorder.record(
                "test_agent",
                "test",
                "Exercise recorder redaction.",
                "Test-only observable rationale.",
                {
                    "token": "SYNTHETIC_TOKEN_SENTINEL",
                    "email": "person@example.test",
                    "account_number": "9" * 12,
                    "path": "/Users/example/private/project",
                },
            )
            text = trajectory.read_text(encoding="utf-8")
            self.assertNotIn("SYNTHETIC_TOKEN_SENTINEL", text)
            self.assertNotIn("person@example.test", text)
            self.assertNotIn("/Users/example", text)
            self.assertNotIn("9" * 12, text)
            self.assertIn("[REDACTED]", text)

            workflow_trajectory = base / "workflow.jsonl"
            report = Coordinator(ROOT).investigate(
                "prompt_injection_log",
                output_dir=base / "reports",
                trajectory_path=workflow_trajectory,
            )[0]
            workflow_text = workflow_trajectory.read_text(encoding="utf-8")
            self.assertNotIn(str(ROOT), workflow_text)
            self.assertNotIn("ignore all previous instructions", workflow_text.lower())
            self.assertNotIn("SYSTEM:", workflow_text)
            self.assertEqual(report.trajectory_path, "workflow.jsonl")

    def test_11_env_example_has_safe_local_defaults_and_no_secret_placeholders(self):
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        assignments = [line for line in text.splitlines() if line and not line.startswith("#")]
        self.assertTrue(assignments)
        for assignment in assignments:
            key, value = assignment.split("=", 1)
            self.assertNotRegex(key, r"(?i)(secret|password|token|api_?key|credential)")
            self.assertNotRegex(value, r"(?i)(https?://|sk-|bearer\s|password|secret)")
            self.assertFalse(Path(value).is_absolute())


if __name__ == "__main__":
    unittest.main()

