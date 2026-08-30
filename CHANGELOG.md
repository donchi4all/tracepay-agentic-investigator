# Improvement changelog

Every metric below comes from the frozen rubric and complete raw case outputs in `evaluation/results/`. No unsuccessful case or regression was removed.

## Submission evidence hardening — 2026-08-30

- **Gap:** representative final trajectories showed the verification agent's instruction and aggregate tool response, but claim-level `verification_feedback` appeared only when a claim was rejected. Because the four representative final cases accept their structurally supported claims, the saved samples did not visibly demonstrate this feedback event.
- **Change:** the verifier now records concise accept/conflict feedback containing only claim ID, structural-check outcome, and final verification status. Tests and Phase 7 require at least one saved `verification_feedback` event. This is observable process metadata, not hidden chain-of-thought.
- **Presentation:** README now has explicit user/bottleneck/value, fair-baseline, safety, and limitations sections. The 4:50 demo has distinct timestamps for the final report, comparison, changelog, highest-impact change, removed experiment, insight, and limitation.
- **Evaluation impact:** no case, gold answer, fixture, diagnostic rule, prediction, report claim, or scoring formula changed. All evaluation modes are rerun below; expected qualitative metrics must remain identical.
- **Decision:** KEEP because it closes an observability evidence gap without adding agent behavior or inflating measured results.

## Judge-grade reproducibility correction — 2026-08-30

- **Finding REPRO-001:** the original `make install` target created a venv but did not install or link TracePay. Its smoke test passed only because Make injected `PYTHONPATH=src`; a plain venv import failed with `ModuleNotFoundError` in the first source-only judge run.
- **Finding REPRO-002:** `scripts/reproduce_all.py` also injected `PYTHONPATH` and copied the ambient environment into its inner subprocesses. It used no third-party package, but this was weaker isolation than the reproduction contract promised.
- **Correction:** added `scripts/install_local.py`, which refuses a global interpreter and writes one venv-local source link; `make install` now creates a pip-free venv and verifies a plain import. Make targets no longer inject `PYTHONPATH`. The all-in-one runner now performs the same local install in its inner pip-free venv and passes only `LANG`, `PATH`, `PYTHONDONTWRITEBYTECODE`, and `PYTHONNOUSERSITE` to judged subprocesses.
- **Clean rerun:** a new source-only copy began with no `.venv`, `.env`, cached results, reports, phase checks, or trajectories and an `env -i` process environment. Installation took 2.50 s including host Xcode cache-path warnings; 35/35 tests passed; both 13-case evaluations matched the frozen quality and safety metrics; and full reproduction passed in 2.231 s internally (2.27 s outer wall time).
- **Result integrity:** the correction changed no fixture, case, rubric, gold answer, diagnostic rule, baseline rule, or quality metric. Provider cost remains USD 0.00. Submission artifacts were regenerated after the observability change in a 2.249 s clean inner run.
- **Evidence:** `artifacts/phase-checks/reproducibility.md`, `artifacts/phase-checks/clean-reproduction.txt`, and the summaries/raw outputs under `evaluation/results/`.

## Hostile security/privacy review

- **Finding SEC-001:** observable trajectories and report metadata exposed absolute developer workstation paths. Corrected by persisting repository-relative paths or filenames and applying defense-in-depth local-path redaction in the recorder.
- **Finding SEC-002:** the build-only setuptools requirement was a version range. Corrected by pinning `setuptools==68.2.2`; runtime dependencies remain empty.
- **Tests:** added 11 explicit controls covering synthetic-only data, credential sentinels, injection resistance, adapter immutability, absence of execution capability, redaction, uncertainty, approval labels, dependency/licence inventory, trajectory privacy, and `.env.example`.
- **Current observed result:** focused review 11/11 passed in 0.045 s; full suite 35/35 passed in 0.058 s; clean reproduction passed in 2.249 s. Evidence is saved under `artifacts/phase-checks/`.
- **Residual risk:** regex scanning is not a DLP system, approval labels are not an authorization service, and any future LLM or production connector requires a new threat model.

## Independent audit correction — v1.1

- **Gold protection:** `evaluation/cases/manifest.json` remained byte-for-byte unchanged at SHA-256 `66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1`.
- **Baseline issue:** the initial baseline returned `EMPTY_OR_UNSTRUCTURED_ERROR` when a lookup produced zero records. A fair, gold-independent zero-result rule now returns `NOT_EXIST`, changing baseline root-cause accuracy from 0.8462 to 0.9231.
- **Scoring issue:** v1.0 treated self-declared `verification_status` as evidence support. V1.1 independently checks cited allow-listed structural fields, valid citation IDs, and exact conflict states. Corrected baseline evidence precision is 0.9231 rather than 0.0000; final remains 1.0000.
- **Rubric handling:** the v1.0 hash is preserved in `evaluation/RUBRIC.md`; the corrected v1.1 formula was written before rerunning all modes. Gold answers and required categories did not change.
- **Audit artifacts:** `evaluation/AUDIT.md`, `evaluation/run_audit.py`, and `evaluation/results/audit.json`.
- **Verdict:** PASS WITH LIMITATIONS, principally because the initial pre-final rubric chronology cannot be independently proven without Git history and the synthetic set is not a blind external holdout.

## Stage 0 — fair baseline — KEEP as comparator

- **Hypothesis:** fixed keyword matching is a useful low-complexity starting point for explicit failure codes.
- **Change:** same sanitized evidence collector, ordered keyword scan, fixed report template, citations, and approval-labelled recommendation.
- **Reason:** represents a credible support script without deliberately withholding the data available to the final workflow.
- **Evaluation command:** `make evaluate-baseline`
- **Result artifact:** `evaluation/results/baseline.json`, `baseline_raw.jsonl`
- **Result:** root cause 0.9231; independently checked evidence precision 0.9231; citations 1.0000; contradiction detection 0.0000; usefulness 0.9692; unsafe action 0.0000.
- **Decision:** KEEP as the comparison baseline.
- **Learning:** after adding the fair zero-result rule, explicit codes and absence handling solve 12/13 cases; free-form injection text still wins the first-match rule and conflicts are not detected.

## Stage 1 — evidence collection and structural correlation — KEEP

- **Hypothesis:** correlating source/state fields and excluding free-form messages from diagnosis will improve the primary metric.
- **Change:** added read-only fixture correlation, normalized timeline, allow-listed structural fields, and deterministic state reconciliation.
- **Reason:** the main user bottleneck is reconstructing evidence across components.
- **Evaluation command:** `.venv/bin/python evaluation/run_evaluation.py --mode stage1`
- **Result artifact:** `evaluation/results/stage1.json`, `stage1_raw.jsonl`
- **Result:** root cause 1.0000; citations 0.0000; evidence precision 0.0000; usefulness 0.7846; unsafe action 0.0000.
- **Decision:** KEEP.
- **Learning:** this was the highest-impact primary-metric change (12/13 to 13/13), but correct prose is not yet an auditable report.

## Stage 2 — structured claims and citations — KEEP

- **Hypothesis:** an evidence/claim contract will make conclusions traceable without changing diagnostic accuracy.
- **Change:** added evidence IDs, provenance, integrity hashes, typed classifications, and supporting/contradicting ID lists.
- **Reason:** every material claim must be reviewable against an exact fixture record.
- **Evaluation command:** `.venv/bin/python evaluation/run_evaluation.py --mode stage2`
- **Result artifact:** `evaluation/results/stage2.json`, `stage2_raw.jsonl`
- **Result:** root cause 1.0000; citations 1.0000; independently checked evidence precision 1.0000; usefulness 0.9846.
- **Decision:** KEEP.
- **Learning:** independently scoring structural support shows the Stage 2 claims are supported, but the runtime workflow still lacks a component that enforces rejection before reporting.

## Stage 3 — semantic verification and contradiction handling — KEEP

- **Hypothesis:** a separate structural verifier will block citation laundering and correctly calibrate conflicts.
- **Change:** added ID validation, structural semantic checks, rejected-claim tracking, explicit conflict detection, and confidence caps.
- **Reason:** a valid evidence ID can still be irrelevant to a claim.
- **Evaluation command:** `.venv/bin/python evaluation/run_evaluation.py --mode stage3`
- **Result artifact:** `evaluation/results/stage3.json`, `stage3_raw.jsonl`
- **Result:** root cause 1.0000; evidence precision 1.0000; citations 1.0000; contradiction detection 1.0000; usefulness 1.0000; unsafe action 0.0000.
- **Decision:** KEEP.
- **Learning:** verification does not raise already-correct Stage 2 evidence precision, but it enforces rejection in the runtime path and raises contradiction detection from 0.0000 to 1.0000.

## Stage 4 — unconstrained hypothesis fan-out — REMOVE

- **Hypothesis:** adding three broad alternative hypotheses might improve coverage on ambiguous cases.
- **Change:** appended unverified network, customer-input, and maintenance guesses after the verified diagnosis.
- **Reason:** tested whether extra hypothesis breadth helped the reviewer.
- **Evaluation command:** `.venv/bin/python evaluation/run_evaluation.py --mode stage4_removed`
- **Result artifact:** `evaluation/results/stage4_removed.json`, `stage4_removed_raw.jsonl`
- **Result:** root cause stayed 1.0000, but evidence precision regressed to 0.2642, citation completeness to 0.3036, and usefulness to 0.8000.
- **Decision:** **REMOVE** from final.
- **Learning:** speculative fan-out created generic noise, violated the material-claim quality bar, and provided no primary-metric benefit.

## Final — evidence-supported architecture

- **Hypothesis:** Stages 1–3 without fan-out give the best measured balance.
- **Change:** retained correlation, contracts, and verification; removed Stage 4 additions.
- **Evaluation command:** `make evaluate-final`
- **Result artifact:** `evaluation/results/final.json`, `final_raw.jsonl`
- **Result:** root cause 1.0000; evidence precision 1.0000; citations 1.0000; contradiction detection 1.0000; usefulness 1.0000; unsafe action 0.0000; provider cost $0.00/case.
- **Decision:** KEEP as final.
