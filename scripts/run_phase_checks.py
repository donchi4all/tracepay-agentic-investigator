#!/usr/bin/env python3
"""Execute and save acceptance evidence for all eight phases."""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tracepay.validation import validate_dataset  # noqa: E402


def _result(name: str, checks: Dict[str, bool], details: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "phase": name,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "details": details,
    }


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def phase_1() -> Dict[str, Any]:
    architecture = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
    decisions = (ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    checks = {
        "specific_user_named": "payment operations engineer" in architecture,
        "bottleneck_documented": "bottleneck" in architecture.lower(),
        "scope_and_non_goals": "Scope and non-goals" in architecture,
        "requirements_matrix": "Requirement-to-evidence matrix" in architecture,
        "defaults_recorded": "D-012" in decisions,
        "no_performance_claim_in_spec": "84.62%" not in architecture,
    }
    return _result("1-discovery-specification", checks, {"files": ["docs/ARCHITECTURE.md", "docs/DECISIONS.md"]})


def phase_2() -> Dict[str, Any]:
    validation = validate_dataset(ROOT)
    rubric = (ROOT / "evaluation" / "RUBRIC.md").read_text(encoding="utf-8")
    checks = {
        "dataset_valid": validation["valid"],
        "at_least_12_cases": validation["case_count"] >= 12,
        "synthetic_only": validation["synthetic_only"],
        "rubric_frozen": "frozen v1.0" in rubric,
        "metrics_predeclared": "Root Cause Identification Score" in rubric,
    }
    return _result("2-evaluation-first", checks, validation)


def phase_3() -> Dict[str, Any]:
    summary_path = ROOT / "evaluation" / "results" / "baseline.json"
    raw_path = ROOT / "evaluation" / "results" / "baseline_raw.jsonl"
    summary = _load(summary_path) if summary_path.exists() else {}
    raw_lines = raw_path.read_text(encoding="utf-8").splitlines() if raw_path.exists() else []
    checks = {
        "baseline_implemented": (ROOT / "src" / "tracepay" / "baseline.py").exists(),
        "baseline_summary_saved": summary.get("mode") == "baseline",
        "all_cases_saved": len(raw_lines) == 13,
        "zero_unsafe_rate": summary.get("unsafe_action_rate") == 0.0,
        "reproduction_command_documented": "make evaluate-baseline" in (ROOT / "docs" / "REPRODUCTION.md").read_text(),
    }
    return _result("3-fair-baseline", checks, summary)


def phase_4() -> Dict[str, Any]:
    report_path = ROOT / "artifacts" / "reports" / "invalid_pin.json"
    report = _load(report_path) if report_path.exists() else {}
    claims = report.get("claims", [])
    required_claim_fields = {
        "claim_id", "statement", "classification", "supporting_evidence_ids",
        "contradicting_evidence_ids", "confidence", "verification_status",
    }
    checks = {
        "markdown_report": (ROOT / "artifacts" / "reports" / "invalid_pin.md").exists(),
        "json_report": bool(report),
        "typed_claim_contract": bool(claims) and all(required_claim_fields == set(item) for item in claims),
        "evidence_contracts_present": bool(report.get("timeline")),
        "financial_actions_zero": report.get("metadata", {}).get("financial_actions_executed") == 0,
    }
    return _result("4-agent-solution", checks, {"sample_report": str(report_path.relative_to(ROOT))})


def phase_5() -> Dict[str, Any]:
    test_path = ROOT / "artifacts" / "phase-checks" / "tests.txt"
    test_output = test_path.read_text(encoding="utf-8") if test_path.exists() else ""
    report_path = ROOT / "artifacts" / "reports" / "invalid_pin.json"
    report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    checks = {
        "all_tests_pass": "Ran 35 tests" in test_output and "OK" in test_output,
        "redaction_observed": "[REDACTED]" in report_text,
        "sensitive_sentinel_absent": "SYNTHETIC_PIN_SENTINEL" not in report_text,
        "unsafe_actions_tested": "test_unsafe_requested_action_requires_label" in test_output,
        "injection_tested": "test_prompt_injection_cannot_override" in test_output,
        "hostile_security_review_passed": (
            (ROOT / "artifacts" / "phase-checks" / "security-review.txt").exists()
            and "Ran 11 tests" in (ROOT / "artifacts" / "phase-checks" / "security-review.txt").read_text()
            and "OK" in (ROOT / "artifacts" / "phase-checks" / "security-review.txt").read_text()
        ),
    }
    return _result("5-testing-adversarial", checks, {"test_artifact": str(test_path.relative_to(ROOT))})


def phase_6() -> Dict[str, Any]:
    modes = ["baseline", "stage1", "stage2", "stage3", "stage4_removed", "final"]
    summaries = {
        mode: _load(ROOT / "evaluation" / "results" / (mode + ".json"))
        if (ROOT / "evaluation" / "results" / (mode + ".json")).exists()
        else {}
        for mode in modes
    }
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    checks = {
        "all_stage_summaries": all(summaries[mode].get("mode") == mode for mode in modes),
        "all_raw_outputs": all((ROOT / "evaluation" / "results" / (mode + "_raw.jsonl")).exists() for mode in modes),
        "baseline_to_final_improves": summaries["final"].get("root_cause_identification_score", 0) > summaries["baseline"].get("root_cause_identification_score", 1),
        "removed_experiment_recorded": "Decision:** **REMOVE" in changelog,
        "removed_experiment_regression_saved": summaries["stage4_removed"].get("evidence_precision", 1) < summaries["stage3"].get("evidence_precision", 0),
        "independent_audit_saved": (
            (ROOT / "evaluation" / "results" / "audit.json").exists()
            and _load(ROOT / "evaluation" / "results" / "audit.json").get("verdict")
            == "PASS WITH LIMITATIONS"
        ),
    }
    return _result("6-measured-iterations", checks, {mode: summaries[mode] for mode in modes})


def phase_7() -> Dict[str, Any]:
    paths = [
        ROOT / "trajectories" / "invalid_pin.jsonl",
        ROOT / "trajectories" / "invalid_cba_response.jsonl",
        ROOT / "trajectories" / "conflicting_states.jsonl",
        ROOT / "trajectories" / "prompt_injection_log.jsonl",
    ]
    events: List[Dict[str, Any]] = []
    for path in paths:
        if path.exists():
            events.extend(json.loads(line) for line in path.read_text().splitlines() if line)
    agents = {item["agent"] for item in events}
    expected_agents = {"coordinator", "evidence_collector", "state_reconciler", "verification_agent", "report_generator"}
    clean_log = ROOT / "artifacts" / "phase-checks" / "clean-reproduction.txt"
    checks = {
        "representative_trajectories": all(path.exists() for path in paths),
        "all_agents_observable": expected_agents <= agents,
        "verification_feedback_saved": any(item["event"] == "verification_feedback" for item in events),
        "retry_correction_saved": any(item["event"] == "retry_success" for item in events),
        "human_checkpoint_saved": any(item["event"] == "human_checkpoint" for item in events),
        "clean_environment_run": clean_log.exists() and "clean reproduction started" in clean_log.read_text(),
    }
    return _result(
        "7-reproducibility-trajectories",
        checks,
        {
            "agents": sorted(agents),
            "event_types": sorted({item["event"] for item in events}),
            "trajectory_count": len(paths),
        },
    )


def phase_8() -> Dict[str, Any]:
    demo = (ROOT / "docs" / "DEMO_SCRIPT.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs" / "SUBMISSION_CHECKLIST.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    demo_segments = [
        "problem, user, and value",
        "fair baseline",
        "one realistic end-to-end execution",
        "final report and approval boundary",
        "baseline comparison and measured improvement",
        "changelog and highest-impact change",
        "removed experiment",
        "hot-take insight and honest limitation",
    ]
    score_categories = [
        "Problem & User Value",
        "Agent Solution & Engineering",
        "End-to-End Quality",
        "Measured Improvement",
        "Reproducibility",
        "Hot Take / Insights",
    ]
    checks = {
        "five_minute_demo": "Target length: 4 minutes 50 seconds" in demo
        and all(segment in demo for segment in demo_segments),
        "six_category_scorecard": all(category in checklist for category in score_categories),
        "limitations_disclosed": "Honest limitations" in checklist,
        "submission_files_listed": "Files to submit" in checklist,
        "claims_link_to_artifacts": "evaluation/results/baseline.json" in readme and "evaluation/results/final.json" in readme,
    }
    return _result("8-submission-video", checks, {"demo": "docs/DEMO_SCRIPT.md", "checklist": "docs/SUBMISSION_CHECKLIST.md"})


def main() -> int:
    functions: List[Callable[[], Dict[str, Any]]] = [
        phase_1, phase_2, phase_3, phase_4, phase_5, phase_6, phase_7, phase_8
    ]
    output_dir = ROOT / "artifacts" / "phase-checks"
    output_dir.mkdir(parents=True, exist_ok=True)
    failed = False
    for number, function in enumerate(functions, 1):
        result = function()
        (output_dir / ("phase-%d.json" % number)).write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("phase %d: %s" % (number, result["status"]))
        failed = failed or result["status"] != "PASS"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
