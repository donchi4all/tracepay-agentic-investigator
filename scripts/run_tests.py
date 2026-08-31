#!/usr/bin/env python3
"""Run standard-library tests and save their real output as a phase artifact."""

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
environment = {
    "LANG": os.environ.get("LANG", "C.UTF-8"),
    "PATH": os.environ.get("PATH", os.defpath),
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONNOUSERSITE": "1",
}
command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
result = subprocess.run(command, cwd=str(ROOT), env=environment, text=True, capture_output=True)
display_command = ["<VIRTUAL_ENV>/bin/python"] + command[1:]
output = "$ %s\n%s%s" % (" ".join(display_command), result.stdout, result.stderr)
artifact = ROOT / "artifacts" / "phase-checks" / "tests.txt"
artifact.parent.mkdir(parents=True, exist_ok=True)
artifact.write_text(output, encoding="utf-8")
print(output, end="")
raise SystemExit(result.returncode)
