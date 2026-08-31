#!/usr/bin/env python3
"""Redact workstation identity and paths from a TracePay terminal transcript."""

import argparse
import re
from pathlib import Path
from typing import Sequence


HEADER = """# Sanitized public-clone terminal evidence

This appendix is supporting execution evidence, not the primary hackathon report. It was captured after cloning the public repository and then sanitized mechanically. User/host identity, repository paths, virtual-environment paths, and temporary directories are replaced with explicit placeholders.

## Runtime provenance

The standalone `make evaluate-baseline` / `make evaluate-final` commands in this transcript measured **0.424042 ms / 0.453333 ms** median runtime. The later isolated `make reproduce-all` run measured **0.302250 ms / 0.387834 ms** and rewrote that clone's saved result files. Both runs have identical qualitative metrics. Runtime is environment-dependent, so these pairs must not be mixed in one results table.

The authoritative primary report uses whichever baseline/final summaries and raw JSONL files are currently saved together in `evaluation/results/`.

<details>
<summary>Show sanitized transcript</summary>

```text
"""

FOOTER = """```

</details>
"""


def sanitize(text: str) -> str:
    text = re.sub(
        r"(?m)^[^@\s]+@[^\s]+\s+tracepay-agentic-investigator\s+%",
        "<USER>@<HOST> <REPOSITORY> %",
        text,
    )
    text = re.sub(
        r"/Users/[^\n]*?/tracepay-agentic-investigator/\.venv",
        "<VIRTUAL_ENV>",
        text,
    )
    text = re.sub(
        r"/Users/[^\n]*?/tracepay-agentic-investigator",
        "<PROJECT_ROOT>",
        text,
    )
    text = re.sub(
        r"/(?:private/)?var/folders/[^\s]+/tracepay-clean-[^/\s]+",
        "<TEMP_DIR>",
        text,
    )
    forbidden = ("/Users/", "/var/folders/", "/private/var/folders/", "donsoft@", "VFDT-")
    remaining = [token for token in forbidden if token in text]
    if remaining:
        raise ValueError("Transcript still contains workstation markers: %s" % remaining)
    return text


def main(argv: Sequence[str] = ()) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv or None)
    sanitized = sanitize(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(HEADER + sanitized.rstrip() + "\n" + FOOTER, encoding="utf-8")
    print("sanitized transcript written: %s" % args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
