# Exact reproduction

## Environment

- Required: CPython 3.9–3.12 and a POSIX-like shell with `make` for convenience.
- Recorded host: CPython 3.9.6, Darwin 25.3.0 arm64.
- Runtime dependencies: none outside the Python standard library.
- Network, secrets, `.env`, containers, and paid APIs: not required.
- Estimated provider cost: exactly USD 0.00 per case; local CPU/electricity excluded.

## Installation semantics

`make install` creates `.venv` without pip and runs `scripts/install_local.py`. TracePay has zero runtime dependencies, so the installer writes one venv-local `.pth` source link instead of invoking pip or a package index. The installer refuses to run outside a virtual environment. The target then imports `tracepay` without `PYTHONPATH`; an import failure fails installation. No global package or package cache is used.

The pinned `setuptools==68.2.2` entry in `pyproject.toml` applies only if someone independently chooses a PEP 517 package-build workflow. The documented judged path does not invoke setuptools.

## One clean command

From the repository root:

```bash
make install
make reproduce-all
```

The script creates a temporary isolated `venv` without pip, installs the same local source link, removes ambient Python/user/provider configuration from every subprocess, runs validation and all tests, evaluates the baseline and five agent stages on the same 13 cases, generates successful/difficult/retry/injection reports and trajectories, and writes phase checks. It removes the temporary environment automatically.

Expected highlights:

```text
dataset: valid=true, case_count=13
tests: Ran 36 tests ... OK
security review: Ran 11 tests ... OK
baseline root_cause_identification_score: 0.9230769230769231
final root_cause_identification_score: 1.0
final unsafe_action_rate: 0.0
audit verdict: PASS WITH LIMITATIONS
clean reproduction: PASS
```

The latest saved repository run took 2.152 seconds internally after adding the deterministic evidence-snapshot regression; the independent source-only audit of commit `2457d07` took 2.193 seconds internally (2.23 seconds outer wall time). Allow approximately 1–5 seconds on a typical local host. Timing metrics may move across hosts; accuracy and safety metrics must match exactly.

## Judge-grade source-only procedure

The following starts with no cached result, hidden `.env`, prior virtual environment, inherited environment variable, or generated trajectory. It deliberately copies only source inputs and declared documentation:

```bash
TRACEPAY_JUDGE_DIR=$(mktemp -d)
mkdir -p "$TRACEPAY_JUDGE_DIR/source" "$TRACEPAY_JUDGE_DIR/home"
rsync -a \
  --exclude '.venv/' --exclude '.env' --exclude '.git/' \
  --exclude '__pycache__/' --exclude '*.pyc' \
  --exclude 'evaluation/results/*' --exclude 'artifacts/reports/*' \
  --exclude 'artifacts/phase-checks/*' --exclude 'trajectories/*' \
  ./ "$TRACEPAY_JUDGE_DIR/source/"
cd "$TRACEPAY_JUDGE_DIR/source"
env -i HOME="$TRACEPAY_JUDGE_DIR/home" TMPDIR="$TRACEPAY_JUDGE_DIR" \
  PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=C.UTF-8 make install
env -i HOME="$TRACEPAY_JUDGE_DIR/home" TMPDIR="$TRACEPAY_JUDGE_DIR" \
  PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=C.UTF-8 make reproduce-all
```

Postconditions:

```bash
env -i HOME="$TRACEPAY_JUDGE_DIR/home" PATH=/usr/bin:/bin:/usr/sbin:/sbin \
  .venv/bin/python -c "import tracepay; print(tracepay.__version__)"
find evaluation/results artifacts/reports artifacts/phase-checks trajectories -type f
```

The import must print `1.0.0` without `PYTHONPATH`. The artifact listing must include baseline/final summaries and raw output, four representative Markdown/JSON reports, four JSONL trajectories, the audit, test logs, and eight phase-check JSON files.

## Individual commands

```bash
make install
make validate-data
make test
make run-baseline CASE=invalid_pin
make investigate CASE=conflicting_states
make evaluate-baseline
make evaluate-final
make audit
make evaluate-all
make phase-checks
```

Direct equivalents without `make`:

```bash
python3 -m venv --without-pip .venv
.venv/bin/python scripts/install_local.py
.venv/bin/python -m tracepay validate-data
.venv/bin/python scripts/run_tests.py
.venv/bin/python -m tracepay baseline invalid_pin
.venv/bin/python -m tracepay investigate conflicting_states
.venv/bin/python evaluation/run_evaluation.py --mode baseline
.venv/bin/python evaluation/run_evaluation.py --mode final
```

Generated artifacts are intentionally saved: evaluation summary JSON and complete raw JSONL under `evaluation/results/`, reports under `artifacts/reports/`, trajectories under `trajectories/`, and acceptance evidence under `artifacts/phase-checks/`.

## Failure diagnosis

- `Unknown case_id`: use a case ID from `evaluation/cases/manifest.json`.
- Python older than 3.9: use CPython 3.9–3.12.
- A metric mismatch with passing tests: confirm `evaluation/RUBRIC.md`, the manifest, and fixture integrity hashes have not changed.
- No `make`: run the direct commands above; installation is a local source link and downloads nothing.
