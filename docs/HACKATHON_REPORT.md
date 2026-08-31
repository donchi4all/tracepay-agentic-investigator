# TracePay hackathon report

## 1. Executive summary

TracePay is a local, deterministic multi-agent workflow that investigates failed **synthetic** payment transactions. It turns records from simulated payment, authentication, approval, and core-banking components into an evidence-grounded Markdown/JSON incident report. It cannot move money: every recommendation is advisory, every consequential next step is labelled `REQUIRES_HUMAN_APPROVAL`, and the observed unsafe-action rate is 0%.

On the same 13 frozen cases, the fair baseline identifies 12/13 root causes and the final workflow identifies 13/13. Complete raw case outputs, a deterministic scorer, and an independent recalculation are saved in `evaluation/results/`. The audit verdict is `PASS WITH LIMITATIONS`.

## 2. User and bottleneck

The primary user is a payment operations engineer investigating one failed transaction. The bottleneck is not access to one error string; it is reconstructing an ordered, defensible account from evidence spread across systems, reconciling contradictory state, preserving what remains unknown, and writing a report another operator can audit.

TracePay's bounded value is one evidence-linked report per investigation. No production time saving, customer outcome, or generalization claim is made because no user study or production trial exists.

## 3. Fair baseline

The baseline receives the same case identifier and sanitized evidence bundle as the final workflow. It receives no gold label. It applies a fixed ordered keyword rule and emits a fixed report template with citations and approval-labelled recommendations.

This is not a deliberately broken comparator: after the independent audit added a generic zero-record rule, it correctly handles 12/13 cases. Its remaining failure is meaningful—the prompt-injection fixture contains `NO_ACTION_REQUIRED` in hostile free-form log text, which wins the baseline's first-match scan. It also does not reconcile the `FAILED`/`POSTED` contradiction.

## 4. Agent architecture and feedback loop

TracePay is deterministic rather than LLM-driven. Its agentic claim is based on explicit orchestration, bounded responsibilities, state passed through typed contracts, tool use, validation feedback, retry, independent verification, and a human checkpoint—not on free-form model narration.

| Role | Observable action | State passed onward |
|---|---|---|
| Coordinator | Publishes `collect → reconcile → verify → report` and invokes each boundary. | Case ID, mode, controlled workflow state. |
| Evidence Collector | Reads the selected fixture through a read-only repository, normalizes timestamps, redacts sensitive-looking values, hashes provenance, and flags instruction-like log data. | Typed sanitized evidence contracts plus security findings. |
| State Reconciler | Orders events, compares structural state/code fields, and emits ranked hypotheses plus FACT/INFERENCE/UNKNOWN claims. | Claims with supporting/contradicting evidence IDs and confidence. |
| Verification Agent | Checks that IDs exist and that allow-listed structural fields semantically support each material statement; rejects unsupported claims or caps conflicted confidence. | Accepted/rejected claim sets, status, and input/output confidence feedback. |
| Report Generator | Renders one verified object to Markdown and JSON, then stops at a human checkpoint. | Auditable report files; no financial action callback exists. |

Representative trajectories contain actions, bounded rationales, tool responses, claim-level `verification_feedback`, malformed-timestamp `validation_feedback` followed by `retry_success`, prompt-injection `security_finding`, and `human_checkpoint`. They intentionally do not contain hidden chain-of-thought.

Why separation mattered: structural correlation moved primary accuracy from 12/13 to 13/13. Verification did not inflate that already-correct Stage 2 prediction score; it enforced claim rejection, raised contradiction detection from 0% to 100%, and made confidence adjustment visible. This distinction is the engineering point.

## 5. Realistic `conflicting_states` execution

Run:

```bash
make investigate CASE=conflicting_states
```

The collector returns a payment-service `FAILED` record and mock-CBA `POSTED` response for the same synthetic transaction. The reconciler routes the case to `TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE`, preserves the authoritative downstream result as UNKNOWN, and creates a factual conflict claim at 100% input confidence. Verification confirms the cited structural conflict, marks the claim `CONFLICTED`, and caps it at 65%; the overall primary assessment remains 62%.

The final report does not call the payment successful or failed authoritatively and does not recommend an automatic retry or reversal. It requests read-only reconciliation behind `REQUIRES_HUMAN_APPROVAL`.

Evidence: `artifacts/reports/conflicting_states.md`, its companion JSON, and `trajectories/conflicting_states.jsonl`.

## 6. Evaluation method

Rubric v1.1 scores exact root-cause class, independently supported material claims, valid citation completeness, contradiction detection, five-part report usefulness, unsafe recommendations, median runtime, and provider cost. There is no LLM judge.

Both systems run once over the same sorted 13-case manifest and fixture records. Gold is read only after a report is produced. Every per-case report, prediction, runtime, and metric component is saved as JSONL. `evaluation/run_audit.py` deliberately does not import the evaluation scorer; it recalculates baseline/final results from report contracts, fixtures, and gold labels.

## 7. Corrected results and audit integrity

The primary table below uses one paired run: the currently saved `evaluation/results/baseline.json` and `final.json`, with the corresponding raw JSONL files. Do not substitute runtime from the public-clone appendix; that is a separately labelled run.

| Metric | Baseline | Final |
|---|---:|---:|
| Root-cause accuracy | 92.31% (12/13) | 100% (13/13) |
| Evidence precision | 92.31% | 100% |
| Citation completeness | 100% | 100% |
| Contradiction detection | 0% | 100% |
| Useful-report score | 96.92% | 100% |
| Unsafe-action rate | 0% | 0% |
| Median runtime | 0.303 ms | 0.396 ms |
| Provider cost per case | $0.00 | $0.00 |

Three audit facts remain prominent:

1. The initial baseline was 84.62% (11/13). The audit found unfair absence handling and added a generic zero-result rule, producing the fair 92.31% baseline without reading gold.
2. Rubric v1.0 trusted self-declared verification status for evidence precision. V1.1 independently checks valid cited IDs and structural semantic support. Gold answers did not change.
3. The gold-manifest SHA-256 remains `66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1`, but no Git history or external timestamp independently proves the initial rubric chronology.

## 8. Improvement changelog and removed experiment

- Stage 1 correlation and structural-field priority produced the primary gain: 12/13 → 13/13.
- Stage 2 added typed claims, evidence IDs, provenance hashes, and citations.
- Stage 3 added semantic verification, rejection, conflict handling, and confidence caps.
- Stage 4 added unconstrained alternative hypotheses. Root accuracy stayed 100%, while evidence precision fell to 26.42%, citation completeness to 30.36%, and usefulness to 80%. It was removed and its regression artifacts were retained.

The lesson is not that more agents or hypotheses are automatically better. Correlation created routing value; verification and removal created trust.

## 9. Security and human approval

All fixtures are authored synthetic records in a `TX-SYN-*` namespace. There are no credentials, production endpoints, customer/account identifiers, network/payment clients, or write-capable adapters. Instruction-like fixture text is treated as untrusted data; diagnosis consumes allow-listed structural fields.

Reports can only write local Markdown/JSON. They cannot execute payment, retry, reversal, block, approval, customer contact, or transaction-state mutation. All recommendations and the final checkpoint use the exact `REQUIRES_HUMAN_APPROVAL` label. The focused hostile suite contains 11 controls; those tests are also included in the 35-test full suite.

## 10. Reproduction

Installation is a deterministic, pip-free local installation that registers the repository source inside an isolated virtual environment. It creates a venv-local `.pth` source link; it does not build a wheel or contact a package index.

```bash
make install
make reproduce-all
```

The runner creates another pip-free temporary venv, registers the source, removes ambient Python/provider configuration, validates data, runs tests/security checks, evaluates all six modes, recalculates the audit, regenerates four reports/trajectories, and writes eight phase checks. Provider/API cost is $0.00; local compute/electricity is excluded and not monetized.

## 11. Limitations and hot take

- The 13 cases are small, synthetic, and authored in the same project. A blind independently authored holdout is still needed.
- Rules target 11 declared failure classes and production connector/authentication/schema/latency behavior is untested.
- `REQUIRES_HUMAN_APPROVAL` is a report contract, not an identity-aware authorization service.
- Clean audit coverage is CPython 3.9.6 on macOS/arm64, not a full platform matrix.
- Runtime microbenchmarks do not measure operator time saved or production capacity.

**Hot take:** an agent system should be rewarded for deleting unsupported possibilities. In this project, hypothesis fan-out made a 100%-accurate system materially worse, while verification improved trust without claiming a new accuracy gain.

## 12. Supporting appendix

- Sanitized public-clone execution: `artifacts/phase-checks/public-clone-transcript.md`.
- Independent evaluation audit: `evaluation/AUDIT.md` and `evaluation/results/audit.json`.
- Source-only reproduction audit: `artifacts/phase-checks/reproducibility.md`.
- Exact commands: `docs/REPRODUCTION.md`.
- Under-five-minute presentation: `docs/DEMO_SCRIPT.md`.
