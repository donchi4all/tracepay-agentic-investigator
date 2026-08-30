"""TracePay command-line interface."""

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from .baseline import run_baseline
from .coordinator import Coordinator
from .validation import validate_dataset


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_baseline(report: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / ("baseline_%s.json" % report["case_id"])
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _display_path(path: Optional[Path], root: Path) -> str:
    if path is None:
        return ""
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracepay", description="Investigate synthetic failed payment transactions"
    )
    parser.add_argument("--root", type=Path, default=project_root(), help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-data", help="validate frozen synthetic fixtures")
    baseline = subparsers.add_parser("baseline", help="run the fair keyword baseline")
    baseline.add_argument("case_id")
    baseline.add_argument("--output-dir", type=Path, default=Path("artifacts/reports"))

    investigate = subparsers.add_parser("investigate", help="run the final agent workflow")
    investigate.add_argument("case_id")
    investigate.add_argument("--output-dir", type=Path, default=Path("artifacts/reports"))
    investigate.add_argument("--trajectory", type=Path)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if args.command == "validate-data":
        result = validate_dataset(root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["valid"] else 1
    if args.command == "baseline":
        report = run_baseline(root, args.case_id)
        output = _write_baseline(report, (root / args.output_dir).resolve())
        print("baseline case=%s class=%s report=%s" % (
            args.case_id, report["primary_failure_class"], _display_path(output, root)
        ))
        return 0
    if args.command == "investigate":
        trajectory = args.trajectory or Path("trajectories/%s.jsonl" % args.case_id)
        report, markdown, json_path = Coordinator(root).investigate(
            args.case_id,
            mode="final",
            output_dir=(root / args.output_dir).resolve(),
            trajectory_path=(root / trajectory).resolve(),
        )
        print(
            "investigation case=%s class=%s confidence=%.2f markdown=%s json=%s"
            % (
                args.case_id,
                report.primary_failure_class.value,
                report.confidence,
                _display_path(markdown, root),
                _display_path(json_path, root),
            )
        )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
