#!/usr/bin/env python3
"""Reproduce every judged artifact in an isolated temporary Python environment."""

import os
import subprocess
import tempfile
import time
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "artifacts" / "phase-checks" / "clean-reproduction.txt"


def append(message: str) -> None:
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(message)
        if not message.endswith("\n"):
            handle.write("\n")


def run(python: Path, arguments: list) -> None:
    # Do not inherit PYTHONPATH, user-site settings, credentials, provider
    # configuration, or any other ambient state into the judged subprocesses.
    environment = {
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "PATH": os.environ.get("PATH", os.defpath),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
    }
    command = [str(python)] + arguments
    result = subprocess.run(
        command, cwd=str(ROOT), env=environment, text=True, capture_output=True
    )
    block = "$ %s\n%s%s" % (" ".join(command), result.stdout, result.stderr)
    print(block, end="")
    append(block)
    if result.returncode:
        append("clean reproduction: FAIL command_exit=%d" % result.returncode)
        raise SystemExit(result.returncode)


def main() -> int:
    started = time.perf_counter()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text("clean reproduction started\n", encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="tracepay-clean-") as directory:
        environment_dir = Path(directory) / "venv"
        venv.EnvBuilder(with_pip=False, clear=True).create(str(environment_dir))
        python = environment_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run(python, ["scripts/install_local.py"])
        run(python, ["-m", "tracepay", "validate-data"])
        run(python, ["scripts/run_tests.py"])
        run(python, ["scripts/run_security_review.py"])
        for mode in ("baseline", "stage1", "stage2", "stage3", "stage4_removed", "final"):
            run(python, ["evaluation/run_evaluation.py", "--mode", mode])
        run(python, ["evaluation/run_audit.py"])
        for case_id in (
            "invalid_pin",
            "invalid_cba_response",
            "conflicting_states",
            "prompt_injection_log",
        ):
            run(python, ["-m", "tracepay", "investigate", case_id])
        run(python, ["scripts/run_phase_checks.py"])
    duration = time.perf_counter() - started
    message = "clean reproduction: PASS duration_seconds=%.3f provider_cost_usd=0.00\n" % duration
    print(message, end="")
    append(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
