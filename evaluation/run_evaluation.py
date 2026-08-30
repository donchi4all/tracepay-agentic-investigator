#!/usr/bin/env python3
"""Run the frozen deterministic rubric against baseline or an experiment stage."""

import argparse
import hashlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tracepay.baseline import run_baseline  # noqa: E402
from tracepay.coordinator import Coordinator  # noqa: E402
from tracepay.repository import FixtureRepository  # noqa: E402
from tracepay.safety import recommendations_are_safe  # noqa: E402


MODES = ("baseline", "stage1", "stage2", "stage3", "stage4_removed", "final")


def _divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


STRUCTURAL_CODE_FIELDS = ("error_code", "reason_code", "rule_code")


def _cited_evidence(report: Dict[str, Any], claim: Dict[str, Any]) -> List[Dict[str, Any]]:
    by_id = {item["evidence_id"]: item for item in report.get("timeline", [])}
    return [
        by_id[item_id]
        for item_id in claim.get("supporting_evidence_ids", [])
        if item_id in by_id
    ]


def _has_structural_code(evidence: List[Dict[str, Any]], expected: str) -> bool:
    return any(
        str(item.get("sanitized_payload", {}).get(field, "")).upper() == expected
        for item in evidence
        for field in STRUCTURAL_CODE_FIELDS
    )


def _root_claim_supported(
    failure_class: str, evidence: List[Dict[str, Any]]
) -> bool:
    explicit_codes = {
        "INVALID_PIN",
        "INVALID_2FA_TOKEN",
        "INVALID_CBA_RESPONSE_DATA",
        "FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED",
        "FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED",
        "FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED",
        "DUPLICATE_OR_ALREADY_PROCESSED_REQUEST",
    }
    if failure_class in explicit_codes:
        return _has_structural_code(evidence, failure_class)
    if failure_class == "NOT_EXIST":
        return any(
            item.get("event_type") == "SEARCH_RESULT"
            and item.get("sanitized_payload", {}).get("matched_records") == 0
            for item in evidence
        )
    if failure_class == "NO_ACTION_REQUIRED":
        if _has_structural_code(evidence, failure_class):
            return True
        states = {
            (
                item.get("source_system"),
                str(item.get("sanitized_payload", {}).get("state", "")).upper(),
            )
            for item in evidence
        }
        return ("payment_service", "COMPLETED") in states and ("mock_cba", "POSTED") in states
    if failure_class == "EMPTY_OR_UNSTRUCTURED_ERROR":
        return any(
            item.get("sanitized_payload", {}).get("error") == {}
            or (
                str(item.get("sanitized_payload", {}).get("state", "")).upper()
                in ("FAILED", "DENIED")
                and not any(item.get("sanitized_payload", {}).get(field) for field in STRUCTURAL_CODE_FIELDS)
            )
            for item in evidence
        )
    if failure_class == "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE":
        if any(
            "TIMEOUT" in (
                item.get("event_type", "")
                + " "
                + str(item.get("sanitized_payload", {}).get("error_code", ""))
                + " "
                + str(item.get("sanitized_payload", {}).get("reason_code", ""))
            ).upper()
            for item in evidence
        ):
            return True
        states = {
            (
                item.get("source_system"),
                str(item.get("sanitized_payload", {}).get("state", "")).upper(),
            )
            for item in evidence
        }
        return ("payment_service", "FAILED") in states and ("mock_cba", "POSTED") in states
    return False


def _claim_semantically_supported(
    report: Dict[str, Any], claim: Dict[str, Any]
) -> bool:
    evidence = _cited_evidence(report, claim)
    if not evidence:
        return False
    claim_id = str(claim.get("claim_id", ""))
    if claim_id in ("CLM-ROOT", "BASE-ROOT"):
        return _root_claim_supported(str(report.get("primary_failure_class", "")), evidence)
    if claim_id == "CLM-CONFLICT":
        states = {
            (
                item.get("source_system"),
                str(item.get("sanitized_payload", {}).get("state", "")).upper(),
            )
            for item in evidence
        }
        return ("payment_service", "FAILED") in states and ("mock_cba", "POSTED") in states
    return False


def _validly_cited(report: Dict[str, Any], claim: Dict[str, Any]) -> bool:
    evidence_ids = {item["evidence_id"] for item in report.get("timeline", [])}
    citations = claim.get("supporting_evidence_ids", []) + claim.get(
        "contradicting_evidence_ids", []
    )
    return bool(citations) and all(item_id in evidence_ids for item_id in citations)


def _verified_contradiction(report: Dict[str, Any]) -> bool:
    if not report.get("contradictions"):
        return False
    return any(
        claim.get("claim_id") == "CLM-CONFLICT"
        and _validly_cited(report, claim)
        and _claim_semantically_supported(report, claim)
        for claim in report.get("claims", [])
    )


def score_case(report: Dict[str, Any], gold: Dict[str, Any]) -> Dict[str, Any]:
    claims = report.get("claims", [])
    material = [
        item for item in claims if item.get("classification") in ("FACT", "INFERENCE")
    ]
    supported = [
        item
        for item in material
        if _validly_cited(report, item) and _claim_semantically_supported(report, item)
    ]
    cited = [item for item in claims if _validly_cited(report, item)]
    safe, unsafe_indexes = recommendations_are_safe(report.get("recommendations", []))
    contradiction_detected = _verified_contradiction(report)
    correct = report.get("primary_failure_class") == gold["failure_class"]
    all_cited = len(cited) == len(claims) if claims else False
    contradiction_point = contradiction_detected if gold["has_contradiction"] else True
    unknown_point = bool(report.get("unknowns")) if gold["requires_unknown"] else True
    useful_points = sum((correct, all_cited, contradiction_point, unknown_point, safe))
    return {
        "root_cause_correct": correct,
        "evidence_supported_claims": len(supported),
        "evidence_material_claims": len(material),
        "cited_claims": len(cited),
        "all_claims": len(claims),
        "unsafe_action": not safe,
        "unsafe_recommendation_indexes": unsafe_indexes,
        "contradiction_eligible": bool(gold["has_contradiction"]),
        "contradiction_detected": contradiction_detected,
        "useful_points": useful_points,
        "useful_max": 5,
    }


def evaluate(project_root: Path, mode: str) -> Dict[str, Any]:
    repository = FixtureRepository(project_root)
    coordinator = Coordinator(project_root)
    rows: List[Dict[str, Any]] = []
    runtimes: List[float] = []

    for definition in sorted(repository.case_definitions(), key=lambda item: item["case_id"]):
        case_id = definition["case_id"]
        started = time.perf_counter()
        if mode == "baseline":
            report = run_baseline(project_root, case_id)
        else:
            report = coordinator.investigate(case_id, mode=mode)[0].to_dict()
        runtime_ms = (time.perf_counter() - started) * 1000.0
        runtimes.append(runtime_ms)
        scores = score_case(report, definition["gold"])
        rows.append(
            {
                "case_id": case_id,
                "categories": definition["categories"],
                "gold": definition["gold"],
                "prediction": report["primary_failure_class"],
                "runtime_ms": runtime_ms,
                "scores": scores,
                "report": report,
            }
        )

    case_count = len(rows)
    material_count = sum(item["scores"]["evidence_material_claims"] for item in rows)
    supported_count = sum(item["scores"]["evidence_supported_claims"] for item in rows)
    claim_count = sum(item["scores"]["all_claims"] for item in rows)
    cited_count = sum(item["scores"]["cited_claims"] for item in rows)
    contradiction_rows = [item for item in rows if item["scores"]["contradiction_eligible"]]
    rubric_path = project_root / "evaluation" / "RUBRIC.md"
    summary = {
        "mode": mode,
        "rubric_version": "1.1-audit-corrected",
        "rubric_sha256": hashlib.sha256(rubric_path.read_bytes()).hexdigest(),
        "executed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "case_count": case_count,
        "root_cause_identification_score": _divide(
            sum(item["scores"]["root_cause_correct"] for item in rows), case_count
        ),
        "evidence_precision": _divide(supported_count, material_count),
        "citation_completeness": _divide(cited_count, claim_count),
        "unsafe_action_rate": _divide(
            sum(item["scores"]["unsafe_action"] for item in rows), case_count
        ),
        "contradiction_detection_rate": _divide(
            sum(item["scores"]["contradiction_detected"] for item in contradiction_rows),
            len(contradiction_rows),
        ),
        "useful_report_score": _divide(
            sum(item["scores"]["useful_points"] for item in rows),
            sum(item["scores"]["useful_max"] for item in rows),
        ),
        "median_runtime_ms": statistics.median(runtimes),
        "estimated_cost_usd_per_case": 0.0,
        "resource_note": "Local standard-library Python only; no network or paid provider calls.",
    }
    return {"summary": summary, "cases": rows}


def write_results(project_root: Path, mode: str, result: Dict[str, Any]) -> None:
    output_dir = project_root / "evaluation" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / (mode + ".json")
    raw_path = output_dir / (mode + "_raw.jsonl")
    summary_path.write_text(
        json.dumps(result["summary"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with raw_path.open("w", encoding="utf-8") as handle:
        for row in result["cases"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv: Sequence[str] = ()) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=MODES, required=True)
    args = parser.parse_args(argv or None)
    result = evaluate(PROJECT_ROOT, args.mode)
    write_results(PROJECT_ROOT, args.mode, result)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
