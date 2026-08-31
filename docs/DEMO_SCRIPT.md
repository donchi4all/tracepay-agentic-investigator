# Five-minute demo script

Target length: 4 minutes 50 seconds. Keep command output pre-generated in case screen recording is slower; do not edit or imply a result that differs from the saved artifacts.

## 0:00–0:30 — problem, user, and value

“TracePay is for a payment operations engineer investigating one failed transaction. Today, evidence lives in payment, auth, approval, and core-banking records. The engineer manually reconstructs a timeline and may still write an unsupported conclusion. TracePay turns that into a reproducible, evidence-verified report without touching financial state.” Show the README problem and architecture.

## 0:30–0:55 — fair baseline

Show `evaluation/RUBRIC.md` and `evaluation/cases/manifest.json`. Explain that the rubric was declared frozen before the initial final run, but that chronology cannot be independently proven because the original workspace has no Git history. All 13 cases are synthetic, and gold labels never enter either implementation. Run:

```bash
make run-baseline CASE=prompt_injection_log
```

Show that the fair first-match baseline is useful on explicit codes but is fooled by `NO_ACTION_REQUIRED` inside hostile free-form log text.

## 0:55–1:35 — one realistic end-to-end execution

Run:

```bash
make investigate CASE=conflicting_states
```

Say what is observable while it runs: coordinator plan, read-only evidence collection, state reconciliation, structural verification, and report generation. The input is one frozen synthetic case; no gold object enters the workflow.

## 1:35–2:10 — final report and approval boundary

Open `artifacts/reports/conflicting_states.md`. Walk through the exact `FAILED` payment record and `POSTED` mock-CBA record, the 62% calibrated assessment, contradiction, unknown downstream outcome, and approval-labelled read-only reconciliation step. Point to `REQUIRES_HUMAN_APPROVAL` and state that the report cannot retry, reverse, approve, block, or mutate a transaction.

## 2:10–2:40 — observable trajectory, verification feedback, and retry

Open `trajectories/conflicting_states.jsonl` and show coordinator plan, collector tool response, diagnostic response, claim-level `verification_feedback`, reporter approval checkpoint, and completion. Point out that `CLM-CONFLICT` moves from input confidence 1.0 to output confidence 0.65 with status `CONFLICTED`; this is a real verifier correction, while the overall diagnosis remains 0.62. Then show `trajectories/invalid_cba_response.jsonl` for malformed-timestamp feedback and the explicit `received_at` retry. State that these are actions, bounded rationales, and results—not hidden chain-of-thought.

## 2:40–3:10 — baseline comparison and measured improvement

Show baseline and final result JSON side-by-side. Highlight 12/13 to 13/13 root-cause identification; independently checked evidence precision 92.31% to 100%; contradiction detection 0% to 100%; and unsafe action rate at 0% for both. State all three audit disclosures: the fair baseline was corrected from 11/13 to 12/13, evidence scoring was independently corrected, and pre-final rubric chronology cannot be externally proven. Gold did not change. Mention deterministic provider cost of $0.00 per case.

## 3:10–3:35 — changelog and highest-impact change

Show `CHANGELOG.md`. Correlation and structural field priority were the highest-impact primary-metric change: 12/13 to 13/13. Verification was the largest enforcement improvement: it raised contradiction detection from 0% to 100% and prevents unsupported claims from reaching the final accepted set.

## 3:35–4:00 — removed experiment

Show Stage 4 in `CHANGELOG.md` and `evaluation/results/stage4_removed.json`. The fan-out experiment kept root-cause accuracy at 100% but reduced citation completeness to 30.36%, evidence precision to 26.42%, and usefulness to 80%. It was removed rather than hidden because extra plausible hypotheses made the report worse.

## 4:00–4:25 — hot-take insight and honest limitation

“More agent output is not more agent value. In this evaluation, correlation produced the accuracy gain, while verification and aggressive removal of unsupported alternatives produced trust. The limitation is equally important: this is a 13-case, self-authored synthetic set, not a blind holdout or production user study; the result does not prove generalization or time savings.”

## 4:25–4:50 — reproducibility and close

Run or point to:

```bash
make reproduce-all
```

Show `artifacts/phase-checks/clean-reproduction.txt`, the eight PASS phase files, and the independent `87/100 — READY WITH LIMITATIONS` headline in `docs/FINAL_COMPETITION_READINESS.md`. If the earlier 91 appears, call it the historical repository self-assessment. Close with the actual boundary: standard-library local execution, provider cost $0.00, no production connectors or load test, and a human still decides every consequential action.
