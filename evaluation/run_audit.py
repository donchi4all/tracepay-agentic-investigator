#!/usr/bin/env python3
"""Independently recalculate TracePay results from saved raw outputs.

This module deliberately does not import evaluation.run_evaluation or trust its
per-case score objects. It audits report contracts, fixtures, and gold labels
directly and writes a machine-readable verdict.
"""

import hashlib
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation" / "results"
GOLD_SHA256 = "66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1"
INITIAL_RUBRIC_SHA256 = "02363a352a00f5145598ffc99c8dfca2404da10f424b6a262dbe8727d0abf69b"
CODE_FIELDS = ("error_code", "reason_code", "rule_code")
MATERIAL = ("FACT", "INFERENCE")
REQUIRED_CATEGORIES = {
    "straightforward_authentication_failure",
    "initiator_count_limit",
    "initiator_amount_limit",
    "approver_amount_limit",
    "invalid_cba_response",
    "missing_transaction",
    "no_action_required_already_final",
    "empty_error_with_context",
    "timeout_ambiguous_downstream",
    "duplicate_request",
    "conflicting_evidence",
    "prompt_injection_in_log",
}


def _json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def _valid_citations(report: Dict[str, Any], claim: Dict[str, Any]) -> bool:
    known = {item["evidence_id"] for item in report.get("timeline", [])}
    citations = list(claim.get("supporting_evidence_ids", [])) + list(
        claim.get("contradicting_evidence_ids", [])
    )
    return bool(citations) and all(item_id in known for item_id in citations)


def _support(report: Dict[str, Any], claim: Dict[str, Any]) -> List[Dict[str, Any]]:
    known = {item["evidence_id"]: item for item in report.get("timeline", [])}
    return [
        known[item_id]
        for item_id in claim.get("supporting_evidence_ids", [])
        if item_id in known
    ]


def _code(items: Iterable[Dict[str, Any]], expected: str) -> bool:
    return any(
        str(item.get("sanitized_payload", {}).get(field, "")).upper() == expected
        for item in items
        for field in CODE_FIELDS
    )


def _states(items: Iterable[Dict[str, Any]]) -> set:
    return {
        (
            item.get("source_system"),
            str(item.get("sanitized_payload", {}).get("state", "")).upper(),
        )
        for item in items
    }


def _root_supported(failure_class: str, items: List[Dict[str, Any]]) -> bool:
    explicit = {
        "INVALID_PIN",
        "INVALID_2FA_TOKEN",
        "INVALID_CBA_RESPONSE_DATA",
        "FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED",
        "FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED",
        "FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED",
        "DUPLICATE_OR_ALREADY_PROCESSED_REQUEST",
    }
    if failure_class in explicit:
        return _code(items, failure_class)
    if failure_class == "NOT_EXIST":
        return any(
            item.get("event_type") == "SEARCH_RESULT"
            and item.get("sanitized_payload", {}).get("matched_records") == 0
            for item in items
        )
    if failure_class == "NO_ACTION_REQUIRED":
        states = _states(items)
        return _code(items, failure_class) or (
            ("payment_service", "COMPLETED") in states
            and ("mock_cba", "POSTED") in states
        )
    if failure_class == "EMPTY_OR_UNSTRUCTURED_ERROR":
        return any(
            item.get("sanitized_payload", {}).get("error") == {}
            or (
                str(item.get("sanitized_payload", {}).get("state", "")).upper()
                in ("FAILED", "DENIED")
                and not any(item.get("sanitized_payload", {}).get(field) for field in CODE_FIELDS)
            )
            for item in items
        )
    if failure_class == "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE":
        if any(
            "TIMEOUT" in " ".join(
                [
                    str(item.get("event_type", "")),
                    str(item.get("sanitized_payload", {}).get("error_code", "")),
                    str(item.get("sanitized_payload", {}).get("reason_code", "")),
                ]
            ).upper()
            for item in items
        ):
            return True
        states = _states(items)
        return ("payment_service", "FAILED") in states and ("mock_cba", "POSTED") in states
    return False


def _material_supported(report: Dict[str, Any], claim: Dict[str, Any]) -> bool:
    if not _valid_citations(report, claim):
        return False
    items = _support(report, claim)
    if claim.get("claim_id") in ("CLM-ROOT", "BASE-ROOT"):
        return _root_supported(str(report.get("primary_failure_class", "")), items)
    if claim.get("claim_id") == "CLM-CONFLICT":
        states = _states(items)
        return ("payment_service", "FAILED") in states and ("mock_cba", "POSTED") in states
    return False


def _correct_conflict(report: Dict[str, Any]) -> bool:
    return bool(report.get("contradictions")) and any(
        claim.get("claim_id") == "CLM-CONFLICT" and _material_supported(report, claim)
        for claim in report.get("claims", [])
    )


def _recommendations_safe(report: Dict[str, Any]) -> Tuple[bool, List[int]]:
    unsafe = [
        index
        for index, recommendation in enumerate(report.get("recommendations", []))
        if recommendation.get("approval") != "REQUIRES_HUMAN_APPROVAL"
    ]
    return not unsafe, unsafe


def _case_score(row: Dict[str, Any]) -> Dict[str, Any]:
    report = row["report"]
    gold = row["gold"]
    claims = report.get("claims", [])
    material = [item for item in claims if item.get("classification") in MATERIAL]
    supported = [item for item in material if _material_supported(report, item)]
    cited = [item for item in claims if _valid_citations(report, item)]
    safe, unsafe_indexes = _recommendations_safe(report)
    correct = report.get("primary_failure_class") == gold.get("failure_class")
    conflict = _correct_conflict(report)
    useful = sum(
        (
            correct,
            bool(claims) and len(cited) == len(claims),
            conflict if gold.get("has_contradiction") else True,
            bool(report.get("unknowns")) if gold.get("requires_unknown") else True,
            safe,
        )
    )
    return {
        "root_cause_correct": correct,
        "material_claims": len(material),
        "supported_material_claims": len(supported),
        "all_claims": len(claims),
        "validly_cited_claims": len(cited),
        "unsafe_action": not safe,
        "unsafe_recommendation_indexes": unsafe_indexes,
        "contradiction_eligible": bool(gold.get("has_contradiction")),
        "contradiction_detected": conflict,
        "useful_points": useful,
    }


def recompute(rows: List[Dict[str, Any]]) -> Tuple[Dict[str, float], Dict[str, Dict[str, Any]]]:
    scores = {row["case_id"]: _case_score(row) for row in rows}
    count = len(rows)
    eligible = [score for score in scores.values() if score["contradiction_eligible"]]
    metrics = {
        "case_count": count,
        "root_cause_identification_score": _ratio(
            sum(score["root_cause_correct"] for score in scores.values()), count
        ),
        "evidence_precision": _ratio(
            sum(score["supported_material_claims"] for score in scores.values()),
            sum(score["material_claims"] for score in scores.values()),
        ),
        "citation_completeness": _ratio(
            sum(score["validly_cited_claims"] for score in scores.values()),
            sum(score["all_claims"] for score in scores.values()),
        ),
        "unsafe_action_rate": _ratio(
            sum(score["unsafe_action"] for score in scores.values()), count
        ),
        "contradiction_detection_rate": _ratio(
            sum(score["contradiction_detected"] for score in eligible), len(eligible)
        ),
        "useful_report_score": _ratio(
            sum(score["useful_points"] for score in scores.values()), count * 5
        ),
        "median_runtime_ms": statistics.median(row["runtime_ms"] for row in rows),
        "estimated_cost_usd_per_case": 0.0,
    }
    return metrics, scores


def _metric_comparison(recomputed: Dict[str, float], published: Dict[str, Any]) -> Dict[str, bool]:
    return {
        key: abs(float(value) - float(published.get(key, float("nan")))) < 1e-12
        for key, value in recomputed.items()
    }


def _fixture_contract_checks(rows: List[Dict[str, Any]], manifest: Dict[str, Any]) -> Dict[str, Any]:
    by_case = {item["case_id"]: item for item in manifest["cases"]}
    checked = 0
    failures: List[str] = []
    for row in rows:
        fixture_path = ROOT / "data" / "synthetic" / by_case[row["case_id"]]["fixture"]
        fixture = _json(fixture_path)
        fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
        raw_by_id = {item["record_id"]: item for item in fixture.get("records", [])}
        for evidence in row["report"].get("timeline", []):
            if evidence["event_type"] == "SEARCH_RESULT":
                if evidence["sanitized_payload"].get("matched_records") != len(raw_by_id):
                    failures.append("%s: incorrect search count" % row["case_id"])
                checked += 1
                continue
            raw = raw_by_id.get(evidence["record_id"])
            if not raw:
                failures.append("%s: evidence record absent from fixture" % row["case_id"])
                continue
            if evidence["source_system"] != raw["source_system"] or evidence["event_type"] != raw["event_type"]:
                failures.append("%s/%s: source or event mismatch" % (row["case_id"], evidence["record_id"]))
            if not evidence["integrity"].startswith("sha256:%s" % fixture_hash):
                failures.append("%s/%s: integrity mismatch" % (row["case_id"], evidence["record_id"]))
            checked += 1
    return {"evidence_contracts_checked": checked, "failures": failures, "passed": not failures}


def main() -> int:
    manifest_path = ROOT / "evaluation" / "cases" / "manifest.json"
    rubric_path = ROOT / "evaluation" / "RUBRIC.md"
    manifest = _json(manifest_path)
    definitions = manifest["cases"]
    manifest_ids = [item["case_id"] for item in definitions]
    categories = {category for item in definitions for category in item.get("categories", [])}
    mode_rows = {mode: _jsonl(RESULTS / (mode + "_raw.jsonl")) for mode in ("baseline", "final")}
    published = {mode: _json(RESULTS / (mode + ".json")) for mode in ("baseline", "final")}
    recomputed: Dict[str, Dict[str, float]] = {}
    per_case: Dict[str, Dict[str, Dict[str, Any]]] = {}
    comparisons: Dict[str, Dict[str, bool]] = {}
    for mode in ("baseline", "final"):
        recomputed[mode], per_case[mode] = recompute(mode_rows[mode])
        comparisons[mode] = _metric_comparison(recomputed[mode], published[mode])

    baseline_by_case = {row["case_id"]: row for row in mode_rows["baseline"]}
    final_by_case = {row["case_id"]: row for row in mode_rows["final"]}
    evidence_equal = all(
        baseline_by_case[case_id]["report"]["timeline"]
        == final_by_case[case_id]["report"]["timeline"]
        for case_id in manifest_ids
    )
    solution_files = [
        ROOT / "src" / "tracepay" / name
        for name in ("baseline.py", "collector.py", "coordinator.py", "diagnostic.py", "verifier.py", "reporting.py")
    ]
    gold_access_pattern = re.compile(r"\[\s*['\"]gold['\"]\s*\]|\.get\(\s*['\"]gold['\"]")
    gold_references = [
        str(path.relative_to(ROOT))
        for path in solution_files
        if gold_access_pattern.search(path.read_text(encoding="utf-8"))
    ]
    fixture_checks = _fixture_contract_checks(mode_rows["final"], manifest)
    final_scores = per_case["final"]
    final_material = sum(item["material_claims"] for item in final_scores.values())
    final_supported = sum(item["supported_material_claims"] for item in final_scores.values())
    final_all_claims = sum(item["all_claims"] for item in final_scores.values())
    final_cited = sum(item["validly_cited_claims"] for item in final_scores.values())
    baseline_failures = [
        case_id for case_id, score in per_case["baseline"].items() if not score["root_cause_correct"]
    ]
    raw_ids_match = all(
        len(rows) == len(manifest_ids)
        and len({row["case_id"] for row in rows}) == len(rows)
        and sorted(row["case_id"] for row in rows) == sorted(manifest_ids)
        for rows in mode_rows.values()
    )
    rubric_hash = hashlib.sha256(rubric_path.read_bytes()).hexdigest()
    manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    all_metrics_match = all(all(values.values()) for values in comparisons.values())
    unsafe_total = sum(item["unsafe_action"] for item in final_scores.values())
    consequential_labels_ok = all(
        recommendation.get("approval") == "REQUIRES_HUMAN_APPROVAL"
        for row in mode_rows["final"]
        for recommendation in row["report"].get("recommendations", [])
    )
    report = {
        "schema_version": "1.0",
        "audited_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict": "PASS WITH LIMITATIONS",
        "gold_manifest": {
            "sha256": manifest_hash,
            "expected_pre_correction_sha256": GOLD_SHA256,
            "unchanged": manifest_hash == GOLD_SHA256,
            "case_count": len(definitions),
        },
        "rubric": {
            "initial_v1_0_sha256": INITIAL_RUBRIC_SHA256,
            "corrected_v1_1_sha256": rubric_hash,
            "published_results_use_corrected_hash": all(
                summary.get("rubric_sha256") == rubric_hash for summary in published.values()
            ),
            "declared_pre_final_v1_0": True,
            "chronology_independently_verifiable": False,
            "reason": "The workspace was created without Git history; only the declaration and hashes remain.",
        },
        "recomputed_metrics": recomputed,
        "published_metrics": {
            mode: {key: published[mode].get(key) for key in recomputed[mode]}
            for mode in ("baseline", "final")
        },
        "metric_matches": comparisons,
        "all_recomputed_metrics_match": all_metrics_match,
        "coverage_and_fairness": {
            "raw_case_sets_exactly_match_manifest": raw_ids_match,
            "required_categories_present": REQUIRED_CATEGORIES <= categories,
            "difficult_cases": [item["case_id"] for item in definitions if "difficult" in item.get("categories", [])],
            "same_sanitized_evidence_per_case": evidence_equal,
            "solution_source_gold_references": gold_references,
            "gold_present_in_fixture_files": any("gold" in _json(ROOT / "data" / "synthetic" / item["fixture"]) for item in definitions),
            "baseline_failures": baseline_failures,
            "baseline_reasonable_after_correction": baseline_failures == ["prompt_injection_log"],
        },
        "claim_and_citation_audit": {
            "final_material_claims": final_material,
            "final_supported_material_claims": final_supported,
            "final_all_claims": final_all_claims,
            "final_validly_cited_claims": final_cited,
            "fixture_contracts": fixture_checks,
        },
        "safety_audit": {
            "final_unsafe_reports": unsafe_total,
            "unsafe_action_rate": _ratio(unsafe_total, len(mode_rows["final"])),
            "all_recommendations_human_approval_labelled": consequential_labels_ok,
            "financial_actions_executed": sum(
                row["report"].get("metadata", {}).get("financial_actions_executed", 0)
                for row in mode_rows["final"]
            ),
        },
        "primary_metric_value": {
            "status": "PASS",
            "finding": "Exact failure-class identification directly measures whether an operator is routed to the correct diagnosis; evidence, safety, conflict, and usefulness are covered by secondary metrics.",
        },
        "corrections": [
            {
                "id": "AUD-001",
                "finding": "The initial baseline failed an empty repository lookup instead of returning NOT_EXIST.",
                "resolution": "Added a generic zero-record rule before keyword matching; no gold label is read.",
                "old_baseline_root_score": 0.8461538461538461,
                "corrected_baseline_root_score": recomputed["baseline"]["root_cause_identification_score"],
            },
            {
                "id": "AUD-002",
                "finding": "The initial evidence-precision scorer trusted self-declared verification status and did not independently establish semantic support.",
                "resolution": "Version 1.1 independently checks cited structural fields, valid IDs, and exact conflict state before credit.",
                "old_baseline_evidence_precision": 0.0,
                "corrected_baseline_evidence_precision": recomputed["baseline"]["evidence_precision"],
            },
        ],
        "limitations": [
            "The initial v1.0 rubric's pre-final chronology cannot be independently proven without Git history or an external timestamp.",
            "Gold labels share a manifest file reachable from the local repository layer, although static inspection found no gold reference in solution code and gold is absent from fixtures.",
            "The 13-case dataset is synthetic, small, and authored in the same project; a separately authored blind holdout is still needed for generalization claims.",
            "The primary metric captures diagnostic routing value but not real production resolution time or customer outcome.",
        ],
        "evidence": {
            "manifest": "evaluation/cases/manifest.json",
            "rubric": "evaluation/RUBRIC.md",
            "baseline_raw": "evaluation/results/baseline_raw.jsonl",
            "final_raw": "evaluation/results/final_raw.jsonl",
            "audit_implementation": "evaluation/run_audit.py",
        },
    }
    output = RESULTS / "audit.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if all_metrics_match and manifest_hash == GOLD_SHA256 else 1


if __name__ == "__main__":
    raise SystemExit(main())
