#!/usr/bin/env python3
"""Install TracePay into the active venv without network or build tools.

The project has no runtime dependencies. This installer writes a venv-local
`.pth` file pointing at the repository's `src` directory, providing editable
source behavior with an empty package cache.
"""

import site
import sys
from pathlib import Path


def main() -> int:
    if sys.prefix == sys.base_prefix:
        raise RuntimeError("Refusing to install outside a virtual environment")
    root = Path(__file__).resolve().parents[1]
    source = (root / "src").resolve()
    candidates = [Path(path) for path in site.getsitepackages()]
    if not candidates:
        raise RuntimeError("No venv site-packages directory was found")
    destination = candidates[0] / "tracepay-local.pth"
    destination.write_text(str(source) + "\n", encoding="utf-8")
    print("Installed TracePay source link: %s" % destination)
    print("Runtime dependencies installed: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
