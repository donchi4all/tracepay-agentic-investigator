"""Professional Markdown and JSON incident report rendering."""

import json
from pathlib import Path
from typing import Dict, List, Tuple

from .models import InvestigationReport
from .trajectory import TrajectoryRecorder


def _bullets(items: List[str], empty: str = "None identified.") -> str:
    return "\n".join("- %s" % item for item in items) if items else "- %s" % empty


def render_markdown(report: InvestigationReport) -> str:
    claim_lines = []
    for claim in report.claims:
        citations = claim.supporting_evidence_ids + claim.contradicting_evidence_ids
        claim_lines.append(
            "- **%s — %s — %s (%.0f%%):** %s [%s]"
            % (
                claim.claim_id,
                claim.classification.value,
                claim.verification_status.value,
                claim.confidence * 100,
                claim.statement,
                ", ".join(dict.fromkeys(citations)),
            )
        )

    timeline_lines = []
    for item in report.timeline:
        state = item["sanitized_payload"].get(
            "state",
            item["sanitized_payload"].get(
                "error_code", item["sanitized_payload"].get("matched_records", "observed")
            ),
        )
        timeline_lines.append(
            "| %s | %s | %s | %s | `%s` |"
            % (
                item["timestamp"],
                item["source_system"],
                item["event_type"],
                state,
                item["evidence_id"],
            )
        )

    recommendation_lines = [
        "- **%s:** %s — %s" % (item.approval, item.action, item.rationale)
        for item in report.recommendations
    ]
    hypothesis_lines = [
        "- `%s` — %.0f%% — %s [%s]"
        % (
            item.failure_class.value,
            item.confidence * 100,
            item.rationale,
            ", ".join(item.evidence_ids),
        )
        for item in report.hypotheses
    ]

    return """# TracePay incident report: {case_id}

**Synthetic transaction:** `{transaction_reference}`<br>
**Evidence snapshot:** {generated_at}<br>
**Primary assessment:** `{failure_class}` ({confidence:.0%} confidence)

## Executive summary

{executive_summary}

## Impact

{impact}

## Root-cause assessment

{hypotheses}

## Verified claims

{claims}

## Timeline

| Timestamp | Source | Event | State/result | Evidence |
|---|---|---|---|---|
{timeline}

## Contradictions

{contradictions}

## Unknowns and missing evidence

{unknowns}

Missing source records: {missing_sources}

## Safe next steps

{recommendations}

## Human approval checkpoint

{safety_notice}

## Traceability

Observable trajectory: `{trajectory_path}`. Full sanitized evidence contracts and fixture integrity hashes are preserved in the companion JSON report.
""".format(
        case_id=report.case_id,
        transaction_reference=report.transaction_reference,
        generated_at=report.generated_at,
        failure_class=report.primary_failure_class.value,
        confidence=report.confidence,
        executive_summary=report.executive_summary,
        impact=report.impact,
        hypotheses="\n".join(hypothesis_lines),
        claims="\n".join(claim_lines),
        timeline="\n".join(timeline_lines),
        contradictions=_bullets(report.contradictions),
        unknowns=_bullets(report.unknowns),
        missing_sources=", ".join(report.missing_sources) or "none",
        recommendations="\n".join(recommendation_lines),
        safety_notice=report.safety_notice,
        trajectory_path=report.trajectory_path or "not recorded",
    )


class ReportGenerator:
    def write(
        self,
        report: InvestigationReport,
        output_dir: Path,
        recorder: TrajectoryRecorder,
    ) -> Tuple[Path, Path]:
        recorder.record(
            "report_generator",
            "instruction",
            "Render accepted claims, evidence, uncertainty, and safe next steps.",
            "A payment operations engineer needs both a readable report and an auditable machine contract.",
            {"case_id": report.case_id},
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / (report.case_id + ".json")
        markdown_path = output_dir / (report.case_id + ".md")
        json_path.write_text(
            json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
        recorder.record(
            "report_generator",
            "human_checkpoint",
            "Stop before any consequential financial or customer-impacting action.",
            "TracePay provides recommendations only; a payment operations engineer must review and approve follow-up.",
            {"approval": "REQUIRES_HUMAN_APPROVAL"},
        )
        recorder.record(
            "report_generator",
            "tool_response",
            "Write Markdown and JSON reports.",
            "Both formats were generated from the same verified report object.",
            {"markdown": markdown_path.name, "json": json_path.name},
        )
        return markdown_path, json_path
