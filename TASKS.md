# TracePay task board

Last updated: 2026-08-30

## Active

- None.

## Pending

- None.

## Completed

- [x] Inspected the initial workspace; it was empty and was not a Git repository.
- [x] Chose a deterministic, local-only, standard-library implementation for the judged path.
- [x] Phase 1: specified the user, bottleneck, scope, architecture, decisions, acceptance criteria, and requirement matrix.
- [x] Phase 2: froze the rubric and validated 13 synthetic cases covering every requested category and known class.
- [x] Phase 3: implemented, tested, and saved complete results for the fair keyword baseline.
- [x] Phase 4: implemented the coordinator, collector, diagnostic agent, verifier, reporter, CLI, contracts, and reports.
- [x] Phase 5: passed 20 unit, integration, end-to-end, privacy, and adversarial tests.
- [x] Phase 6: evaluated all stages, retained evidence-supported changes, and removed speculative fan-out.
- [x] Phase 7: passed clean isolated-venv reproduction and saved representative trajectories for every agent.
- [x] Phase 8: completed the scorecard, submission checklist, limitations, and 4:40 demo script.
- [x] All eight acceptance checks passed; evidence is saved in `artifacts/phase-checks/`.
- [x] Independent audit corrected the fair baseline and evidence scorer without changing gold answers, reran all modes, and saved a PASS WITH LIMITATIONS verdict.
- [x] Hostile security review corrected local-path leakage and an unpinned build dependency; 11/11 focused and 35/35 total tests pass.
- [x] Verified from saved artifacts and executable phase checks that Phase 8 is the last genuinely completed build phase; all eight phase JSON files report PASS and their referenced evidence exists.
- [x] Reproduced installation, validation, 35 tests, one baseline case, one final investigation, both complete evaluations, four reports, four trajectories, the audit, and all phase checks in a source-only temporary copy with an empty inherited environment.
- [x] Corrected `make install` after the first judge run proved it was not importable without Make's temporary `PYTHONPATH`; the local offline installer now creates a venv-local source link and verifies a plain import.
- [x] Removed the remaining `PYTHONPATH` and ambient-environment dependency from the clean runner, shell wrapper, and test launchers; the runner now installs into a pip-free venv before executing judged commands.
- [x] Saved the judge-grade clean audit with exact versions, commands, expected/actual output, runtime, cost, defects, corrections, and limitations in `artifacts/phase-checks/reproducibility.md`.
- [x] Regenerated all evaluation modes, reports, representative trajectories, test/security logs, audit output, and eight phase checks after the reproducibility correction.
- [x] Reconciled README, reproduction, security, changelog, and submission-checklist claims with the latest saved artifacts; final regression, focused security, evaluation audit, and phase checks pass.

## Blocked

- Independent proof that rubric v1.0 predates the initial final run is blocked because this directory has no Git history or external timestamp. This remains disclosed in `evaluation/AUDIT.md` and does not justify changing gold labels.
- Recording/uploading the actual demo video and submitting to an external hackathon portal require a human and are outside this local repository task; the under-five-minute script and submission inventory are prepared.
