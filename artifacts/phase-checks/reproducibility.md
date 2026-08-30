# TracePay judge-grade reproducibility audit

Audit date: 2026-08-30  
Verdict: **PASS WITH LIMITATIONS**

## Outcome

TracePay was reproduced from a source-only temporary copy using only `docs/REPRODUCTION.md`. The final rerun began with no virtual environment, `.env`, generated results, reports, phase checks, trajectories, bytecode, or inherited application/provider configuration. Installation, validation, all tests, representative commands, both complete evaluations, the full all-in-one reproduction, reports, and trajectories succeeded.

The first clean attempt exposed a real installation defect, and a subsequent inspection exposed weaker-than-documented isolation in the all-in-one runner. Both were corrected without changing fixtures, gold answers, evaluation rules, baseline behavior, or final diagnostic behavior. This document reports both failures and the successful corrected rerun.

## Clean boundary

The documented source-only procedure was followed with a fresh directory created by `mktemp`. `rsync` excluded `.venv/`, `.env`, `.git/`, `.DS_Store`, Python caches, and every file under `evaluation/results/`, `artifacts/reports/`, `artifacts/phase-checks/`, and `trajectories/`.

Before installation, the audit observed:

- `.venv` absent;
- `.env` absent;
- zero files in all four generated-output directories;
- no Git metadata;
- an `env -i` process containing only the explicitly supplied `HOME`, `TMPDIR`, `PATH`, and `LANG`, plus shell-created `PWD`, `SHLVL`, and `_` bookkeeping;
- no network or package-index command.

The final temporary source root was `/tmp/tracepay-submission.j5anjg/source`. It is recorded so the command evidence is exact; no result depends on that path.

## Exact environment

| Component | Observed version/state |
|---|---|
| TracePay | 1.0.0 |
| CPython | 3.9.6, Clang 17.0.0 |
| OS/kernel | Darwin 25.3.0, arm64 |
| GNU Make | 3.81 |
| zsh | 5.9, arm64-apple-darwin25.0 |
| rsync | openrsync protocol 29 |
| Fresh venv distributions | `[]` |
| Runtime dependencies | 0; Python standard library only |
| Build metadata | `setuptools==68.2.2` pinned, not invoked by the judged path |

After `make install`, a plain `import tracepay` with no `PYTHONPATH` resolved to the temporary copy's `src/tracepay/__init__.py`. `importlib.metadata.distributions()` returned an empty list because the venv was created with `--without-pip`.

The stripped environment caused macOS/Xcode to emit cache-directory fallback warnings during venv creation. They were host tooling warnings, not TracePay failures: the command exited 0, used only the designated temporary tree, and every postcondition passed. Their delay is included in the 2.50-second installation wall time.

## Findings and corrections

### REPRO-001 — install target was not a real installation

The first source-only run executed the then-documented `make install` in 3.42 seconds and returned success, but a separate plain venv `import tracepay` failed with `ModuleNotFoundError`. The Make target had injected `PYTHONPATH=src` into its smoke test and all convenience commands, masking the missing installation.

Correction:

- added `scripts/install_local.py` to create an offline, venv-local `.pth` source link;
- made the installer refuse execution outside a virtual environment;
- removed `PYTHONPATH` injection from Make targets;
- made `make install` create the venv without pip and fail unless a plain import succeeds;
- documented the exact local-install semantics and direct command equivalents.

### REPRO-002 — inner clean runner inherited ambient state

Inspection after the first correction showed that `scripts/reproduce_all.py` still set `PYTHONPATH` and copied the calling environment into its inner subprocesses. This did not change evaluation inputs or use global packages, but it did not meet the stronger clean-environment claim.

Correction:

- the runner now creates an inner pip-free venv and calls `scripts/install_local.py` before any TracePay command;
- it no longer sets `PYTHONPATH`;
- judged subprocesses, including the unittest subprocesses, receive only `LANG`, `PATH`, `PYTHONDONTWRITEBYTECODE=1`, and `PYTHONNOUSERSITE=1`;
- the corrected source-only rerun was repeated from another empty temporary directory.

Neither correction changed evaluation cases, fixture hashes, the gold manifest, rubric hash, predictions, or qualitative metric values. Runtime artifacts were superseded by the rerun, as expected for an environment-dependent metric.

## Commands and observed results

Every command below ran from the fresh temporary source root under:

```text
env -i HOME=/tmp/tracepay-submission.j5anjg/home \
  TMPDIR=/tmp/tracepay-submission.j5anjg/tmp \
  PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=C.UTF-8
```

Wall times are `/usr/bin/time -p` real times. Sub-second values are host-specific.

| Requirement and exact command | Expected from documentation | Actual | Wall time |
|---|---|---|---:|
| Installation: `make install` | pip-free local install; plain import prints version 1.0.0 | PASS; import printed `TracePay 1.0.0 installed on Python 3.9.6`; installed distributions `[]` | 2.50 s |
| Synthetic validation: `make validate-data` | valid, synthetic-only, 13 cases | PASS; `valid=true`, `synthetic_only=true`, `case_count=13`, no errors | 0.10 s |
| Full tests: `make test` | `Ran 35 tests ... OK` | PASS; 35 passed, 0 failed in 0.065 s internal | 0.28 s |
| One baseline: `make run-baseline CASE=invalid_pin` | `INVALID_PIN` and a local JSON report | PASS; `INVALID_PIN`, `artifacts/reports/baseline_invalid_pin.json` | 0.04 s |
| One final investigation: `make investigate CASE=conflicting_states` | ambiguous downstream class, 0.62 confidence, Markdown/JSON | PASS; `TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE`, confidence 0.62, both reports written | 0.05 s |
| Complete baseline: `make evaluate-baseline` | 13 cases; root score 12/13; unsafe rate 0 | PASS; root/evidence 0.9230769231, citations 1.0, contradiction 0.0, usefulness 0.9692307692, unsafe 0.0 | 0.05 s |
| Complete final: `make evaluate-final` | 13 cases; all quality metrics 1.0; unsafe rate 0 | PASS; root/evidence/citations/contradiction/usefulness 1.0, unsafe 0.0 | 0.05 s |
| All artifacts: `make reproduce-all` | install, validate, tests, security, all evaluation modes, audit, four representative investigations, eight phase checks | PASS; internal duration 2.231 s, outer wall time 2.27 s | 2.27 s |

The full reproduction additionally observed 11/11 focused hostile security tests passing in 0.043 seconds, audit verdict `PASS WITH LIMITATIONS`, and all eight phase checks reporting `PASS`.

## Evaluation output verification

The corrected clean all-in-one run regenerated all six modes. Each raw JSONL contained exactly 13 nonempty case records:

- `baseline_raw.jsonl`;
- `stage1_raw.jsonl`;
- `stage2_raw.jsonl`;
- `stage3_raw.jsonl`;
- `stage4_removed_raw.jsonl`;
- `final_raw.jsonl`.

The evaluation audit recomputed every baseline and final aggregate from those raw records and reported `all_recomputed_metrics_match=true`. Baseline and final qualitative results matched the documented frozen claims. The rubric hash remained `4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546`; the unchanged gold-manifest hash remained `66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1`.

Current saved evidence: `evaluation/results/baseline.json`, `evaluation/results/baseline_raw.jsonl`, `evaluation/results/final.json`, `evaluation/results/final_raw.jsonl`, and `evaluation/results/audit.json`.

## Reports and trajectories

Fresh generation produced four final Markdown reports, four corresponding final JSON reports, one baseline JSON report, and four JSONL trajectories:

| Case | Why representative | Observed trajectory evidence |
|---|---|---|
| `invalid_pin` | successful straightforward case | all five agents, human checkpoint, completion |
| `invalid_cba_response` | malformed timestamp/correction path | validation feedback followed by `retry_success` |
| `conflicting_states` | difficult contradictory state | all five agents, human checkpoint, ambiguity retained at 0.62 |
| `prompt_injection_log` | hostile fixture text | `security_finding`; final structural diagnosis remains `INVALID_2FA_TOKEN` |

Across the trajectories, the observed agents were coordinator, evidence collector, state reconciler, verification agent, and report generator. Observed event types included plan, instruction, tool response, validation feedback, retry success, security finding, human checkpoint, and completion. The focused tests also verified redaction, read-only fixtures, no financial mutation capability, uncertainty preservation, and exact `REQUIRES_HUMAN_APPROVAL` labels.

Current saved evidence: `artifacts/reports/`, `trajectories/`, `artifacts/phase-checks/tests.txt`, `artifacts/phase-checks/security-review.txt`, and `artifacts/phase-checks/clean-reproduction.txt`.

## Cost

Provider, API, network, and package-download cost was **USD 0.00**. No network or paid service was invoked. Local CPU and electricity for the 2.27-second run were not metered, so no invented monetary estimate is reported; they remain explicitly excluded from the project cost metric.

## Limitations

- The clean judge run exercised CPython 3.9.6 on macOS/arm64. The declared Python 3.10–3.12 range and other POSIX hosts were not independently exercised here.
- Runtime is too short and environment-dependent to support capacity claims.
- The workspace has no Git history, so this audit can inspect current files but cannot produce a version-control diff or independently prove the original rubric chronology.
- The small synthetic evaluation is reproducible but is not an external blind holdout or production validation.

## Verdict rationale

**PASS WITH LIMITATIONS.** All requested clean-environment operations succeeded after two disclosed reproducibility defects were fixed. The final run used no cached output, hidden file, inherited provider configuration, global package, installed distribution, package index, or `PYTHONPATH`. Generated artifacts and saved metrics match the documented deterministic expectations. The limitations concern untested platform/version breadth, absent Git chronology, and external validity—not a failure of the reproduced judged path.
