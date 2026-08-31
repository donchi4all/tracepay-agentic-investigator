# Submission checklist and scorecard

## Historical repository self-assessment: 91/100

This is a repository self-assessment against the supplied weights, not the independent result or a claim about an organizer's final score. The subsequent fresh-clone audit in `docs/FINAL_COMPETITION_READINESS.md` awarded **87/100 — READY WITH LIMITATIONS**; that is the score to present externally. Points below were withheld where evidence was absent even when the limitation is intentional.

| Judging category | Max | Earned | Evidence-backed rationale |
|---|---:|---:|---|
| Problem & User Value | 15 | **14** | `README.md` and `docs/ARCHITECTURE.md` name the payment operations engineer, multi-system evidence bottleneck, exact report output, and safety boundary. No operator study or measured time-to-resolution evidence exists. |
| Agent Solution & Engineering | 30 | **28** | Five bounded roles, typed evidence/claim/report contracts, read-only tool boundary, semantic verifier, redaction, observable claim feedback, retry, and human checkpoint are implemented in `src/tracepay/` and exercised by tests. Rules and adapters remain deliberately narrow and synthetic. |
| End-to-End Quality | 20 | **18** | One command produces consistent Markdown/JSON reports, trajectories, audit evidence, and safe recommendations across normal, difficult, malformed, conflicting, empty-error, and hostile-log cases. There is no tested production integration or operator-facing authorization/UX. |
| Measured Improvement | 15 | **13** | Same 13 frozen cases, complete raw outputs, deterministic scoring, fair corrected baseline, audit, stage ablations, and a disclosed removed experiment support 12/13 to 13/13. The set is self-authored and small, and initial rubric chronology lacks external proof. |
| Reproducibility | 15 | **14** | Pip-free source-only installation and a sanitized clean runner reproduce tests, evaluation, reports, trajectories, and phase evidence at USD 0 provider cost. Only CPython 3.9.6 on macOS/arm64 was independently exercised. |
| Hot Take / Insights | 5 | **4** | `CHANGELOG.md` demonstrates that structural correlation created the accuracy gain and speculative fan-out degraded evidence quality, supporting “more output is not more value.” The insight is not externally replicated. |
| **Total** | **100** | **91** | Strong local submission with explicit external-validity, chronology, platform, and production-scope limitations. |

## Lost-point ledger

Every withheld point is accounted for below. None can be honestly recovered by editing gold labels or rewording a claim.

| ID | Point | Missing evidence or quality issue | Resolution in this submission |
|---|---:|---|---|
| PV-1 | −1 | No payment-operations user study, measured investigation-time reduction, or production outcome evidence. | Not fabricated. README now explicitly limits the value claim; recovery requires an external user study. |
| ASE-1 | −1 | Deterministic rules target 11 declared failure classes; unseen failure/schema generalization is unproven. | Disclosed in README/checklist. Recovery requires a separately designed blind set, not gold changes. |
| ASE-2 | −1 | Evidence adapters are read-only fixture simulations, not authenticated production connectors with pagination/schema-drift handling. | Kept intentionally safe. Recovery requires a new connector threat model and integration test environment. |
| E2E-1 | −1 | No production-like latency, clock-skew, load, or connector-failure exercise. | Disclosed; cannot be added honestly without a representative external environment. |
| E2E-2 | −1 | CLI/reports have no identity-aware approval service or validated operator UX. | `REQUIRES_HUMAN_APPROVAL` remains an advisory contract; real authorization and UX testing are future work. |
| MI-1 | −1 | Thirteen cases are small, synthetic, and authored in the same project; there is no external blind holdout. | All cases retained and disclosed. Recovery requires independent case authorship and a frozen holdout. |
| MI-2 | −1 | No Git history or external timestamp independently proves initial rubric-before-final chronology. | Audit limitation retained; gold and rubric hashes are preserved rather than rewritten. |
| R-1 | −1 | Clean reproduction was observed on CPython 3.9.6/macOS arm64 only, not the entire declared Python/platform range. | Exact environment recorded. Recovery requires a real CI/platform matrix. |
| HT-1 | −1 | The “less fan-out, more verification” insight is supported only by this synthetic evaluation. | Removed experiment and regression remain visible; external replication is still required. |

## Requirement verification

| Request | PASS/FAIL | Evidence |
|---|---|---|
| Honest weighted score with every lost point explained | **PASS** | This scorecard and lost-point ledger. |
| Fix missing evidence or quality gaps when locally possible | **PASS** | `CHANGELOG.md` submission-hardening entry; explicit verification feedback in `src/tracepay/verifier.py`; updated tests and Phase 7. |
| README covers user, bottleneck, value, baseline, architecture, safety, measured results, reproduction, and limitations | **PASS** | `README.md` named sections and quick start. |
| Changelog contains meaningful experiments, evidence, decisions, and one removed experiment | **PASS** | `CHANGELOG.md`; Stage 0 through Final plus Stage 4 `REMOVE`, audit/security/reproduction corrections. |
| Trajectories cover every agent and observable action, tool response, verification feedback, retry, and approval checkpoint without hidden chain-of-thought | **PASS** | `trajectories/*.jsonl`; `artifacts/phase-checks/phase-7.json`; `tests/test_end_to_end.py`; `tests/test_security_controls.py`. |
| Demo remains under five minutes and timestamps every requested segment | **PASS** | `docs/DEMO_SCRIPT.md`, target 4:50. |
| Every numerical result claim is checked against raw case outputs | **PASS** | `evaluation/results/*_raw.jsonl`, summaries beside them, and `evaluation/results/audit.json` with `all_recomputed_metrics_match=true`. |
| Final test, evaluation, audit, and clean reproduction checks pass | **PASS** | `artifacts/phase-checks/tests.txt`, `security-review.txt`, `clean-reproduction.txt`, all six result pairs, and phase JSON files. |
| Submission checklist has PASS/FAIL and evidence paths for every requirement | **PASS** | This table. |

## Files to submit

- `README.md`, `LICENSE`, `CHANGELOG.md`, `TASKS.md`, `pyproject.toml`, `.env.example`, `.gitignore`
- `src/tracepay/`, `baseline/`, `tests/`, and `scripts/`
- `data/synthetic/` and `evaluation/cases/`
- `evaluation/RUBRIC.md`, runner, summaries, and all raw JSONL results
- `evaluation/AUDIT.md`, `evaluation/run_audit.py`, and `evaluation/results/audit.json`
- `trajectories/` representative JSONL
- `artifacts/reports/` and `artifacts/phase-checks/`
- `artifacts/phase-checks/reproducibility.md` with the independent source-only judge rerun
- `artifacts/phase-checks/public-clone-transcript.md` as sanitized supporting evidence, never the primary report
- `docs/HACKATHON_REPORT.md` as the judge-facing narrative
- all `docs/`

Do not add `.venv`, credentials, real data, production endpoints, or unrelated local files.

## Artifact checklist

- [x] The primary payment-operations user, bottleneck, and bounded value claim are explicit.
- [x] Baseline and final use identical frozen inputs.
- [x] Declared rubric chronology, hashes, and the inability to independently prove initial chronology are all disclosed.
- [x] Thirteen synthetic cases cover every requested category and known class.
- [x] All experiment stages have saved complete case-level evidence.
- [x] Removed experiment and regressions are disclosed.
- [x] Every final material claim has a typed contract and verified citation.
- [x] Successful, difficult, correction/retry, injection, claim-verification-feedback, and human-checkpoint trajectories are saved.
- [x] Tests cover missing/malformed/conflicting/empty/duplicate/injection/unsafe conditions.
- [x] Provider cost is $0.00 and runtime is measured, not estimated from invention.
- [x] New-versus-pre-existing statement and component licences are documented.
- [x] Clean reproduction and phase checks pass.
- [x] A source-only copy with empty generated-output directories and sanitized inherited environment passes installation and full reproduction without `PYTHONPATH` or installed distributions.
- [x] Public terminal evidence replaces user, host, repository, virtual-environment, and temporary paths with explicit placeholders.

## Final observed commands

| Command | Actual result | Saved evidence |
|---|---|---|
| `make test` | 36 passed, 0 failed; 0.058 s internal in the final clean run | `artifacts/phase-checks/tests.txt` |
| `make security-review` | 11 passed, 0 failed; 0.044 s internal in the final clean run | `artifacts/phase-checks/security-review.txt` |
| `make evaluate-all` | Six modes × 13 raw cases; expected qualitative metrics unchanged | `evaluation/results/*.json`, `*_raw.jsonl` |
| `make audit` | Every recomputed baseline/final metric matches; `PASS WITH LIMITATIONS` | `evaluation/results/audit.json` |
| `make reproduce-all` | PASS in 2.152 s internally; reports, trajectories, and all eight phase checks regenerated | `artifacts/phase-checks/clean-reproduction.txt`, `phase-*.json` |

## Honest limitations

1. The diagnostic rules are optimized for the 11 declared failure classes and may classify a novel failure as unstructured/unknown.
2. The fixture repository simulates systems; production connector authentication, latency, pagination, clock skew, and schema drift are not validated.
3. The evaluation set is small and authored with the implementation in mind; a separately authored blind set would strengthen generalization evidence.
4. Runtime numbers are too small for production capacity planning and exclude disk/network latency.
5. The human approval label is a software contract, not an organizational authorization system.
6. No optional LLM mode was added because it was not needed to improve the frozen primary metric and would weaken clean reproducibility.
