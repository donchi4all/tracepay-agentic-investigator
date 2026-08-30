# Independent evaluation audit

**Verdict: PASS WITH LIMITATIONS**  
**Audit date:** 2026-08-29  
**Audited gold-manifest SHA-256:** `66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1`  
**Machine-readable evidence:** `evaluation/results/audit.json`

## Executive finding

The corrected evaluation supports the claim that the final TracePay workflow improves exact root-cause classification over a fair deterministic baseline on the complete 13-case synthetic set: 12/13 (92.31%) versus 13/13 (100%). All final material claims independently match cited structural evidence, all claim citations resolve, the declared conflicting state is correctly detected, and every recommendation requires human approval.

The initial published comparison was not fully valid. The baseline omitted an obvious zero-record lookup rule, and the evidence-precision scorer treated a system's own `verification_status` as proof instead of independently testing semantic support. Both defects were corrected before the audited rerun. The gold manifest remained byte-for-byte unchanged.

The verdict is not an unqualified PASS because the repository has no Git history or external timestamp proving that rubric v1.0 existed before the initial final evaluation. Gold is also stored in a manifest reachable by the repository layer, although static inspection found no solution-code access and fixtures contain no gold. Finally, this is a small, internally authored synthetic set rather than an external blind holdout.

## 1. Rubric chronology and clarity

Rubric v1.0 declares that it was frozen on 2026-08-29 and every initial result recorded the same v1.0 SHA-256, `02363a352a00f5145598ffc99c8dfca2404da10f424b6a262dbe8727d0abf69b`. This is internally consistent, but the initial directory was not a Git repository, so chronology cannot be independently confirmed from commit history or an external timestamp.

The audit found ambiguity in implementation, not the high-level metric name: “verified” evidence precision was scored from a self-declared report status. Rubric v1.1 now states an external structural-support rule, requires all cited IDs to exist, and requires the exact FAILED/POSTED evidence pattern for contradiction credit. V1.1 was written before the corrected reruns. No gold answer or category was changed.

## 2. Baseline/final input equivalence

PASS. Both raw files contain exactly the same 13 unique case IDs as the manifest. For every case, the complete sanitized `timeline` evidence array in baseline output is byte-for-byte equal to the final output, including source, record, timestamp, payload, transaction reference, and fixture-integrity hash. Both paths call the same `EvidenceCollector` and `FixtureRepository`.

The evaluator reads gold only after generating a report. Fixture JSON files contain no `gold` field, and static inspection found no `gold` access in baseline, collector, coordinator, diagnostic, verifier, or reporter source. A residual architectural limitation is that the repository's manifest file itself contains gold and is locally reachable.

## 3. Case coverage

PASS. Thirteen cases exist; no case is duplicated or excluded from raw output.

| Required category | Case evidence |
|---|---|
| Authentication failures | `invalid_pin`, `invalid_2fa` |
| Initiator count/amount and approver amount limits | `initiator_count_limit`, `initiator_amount_limit`, `approver_amount_limit` |
| Invalid CBA response | `invalid_cba_response` |
| Missing transaction | `missing_transaction` |
| Already final / no action | `already_final` |
| Empty error | `empty_error_context` |
| Difficult/ambiguous | `timeout_ambiguous`, `conflicting_states` |
| Duplicate request | `duplicate_request` |
| Conflicting evidence | `conflicting_states` |
| Prompt injection | `prompt_injection_log` |

## 4. Independent metric recalculation

`evaluation/run_audit.py` reads saved raw JSONL, fixtures, and gold directly. It does not import or call `evaluation/run_evaluation.py`, and it ignores saved per-case `scores`. Every recalculated aggregate matches the corrected published JSON exactly.

| Metric | Baseline recalculated | Final recalculated | Published match |
|---|---:|---:|---|
| Cases | 13 | 13 | Yes |
| Root-cause identification | 0.9230769231 | 1.0000000000 | Yes |
| Evidence precision | 0.9230769231 | 1.0000000000 | Yes |
| Citation completeness | 1.0000000000 | 1.0000000000 | Yes |
| Unsafe-action rate | 0.0000000000 | 0.0000000000 | Yes |
| Contradiction detection | 0.0000000000 | 1.0000000000 | Yes |
| Useful-report score | 0.9692307692 | 1.0000000000 | Yes |
| Estimated provider cost/case | $0.00 | $0.00 | Yes |

Median runtime is also recomputed exactly from the 13 raw `runtime_ms` values and compared to each published summary. Runtime is retained in `audit.json` because it varies on each host and rerun.

## 5. Cherry-picking, failures, leakage, and baseline fairness

- **No cherry-picking found:** raw baseline and final outputs each contain all 13 manifest cases exactly once. The lone corrected baseline failure, `prompt_injection_log`, remains visible.
- **No excluded failures found:** aggregate denominators are 13; case-level failure flags reconcile to each numerator.
- **No observed gold leakage:** the gold-manifest hash did not change, fixture files contain no gold, and solution code does not reference gold. The shared manifest location remains a design limitation.
- **Initial baseline fairness issue corrected:** a normal record lookup baseline should distinguish zero results from a failure record. A generic `if no records: NOT_EXIST` rule was added without reading gold, raising baseline accuracy from 11/13 to 12/13.
- **Corrected baseline is reasonable:** it handles zero results and all explicit known codes. It still fails prompt injection because a simple first-match keyword method scans free-form log content; that is a genuine, documented baseline limitation rather than an artificial omission.

## 6. Primary metric and user value

PASS. Exact failure-class identification directly tests whether a payment operations engineer is routed to the correct diagnosis class. It is a reasonable primary metric for the stated bottleneck, but it does not by itself measure report trust, safety, or resolution quality. The predeclared citation, evidence, conflict, usefulness, runtime, and unsafe-action secondary metrics cover those dimensions. No claim is made about real production resolution time or customer outcome.

## 7. Claim and citation verification

PASS on the corrected final raw output.

- 14/14 FACT or INFERENCE claims are supported by their cited allow-listed fixture fields.
- 17/17 total claims, including UNKNOWN claims, have only valid evidence IDs.
- 49/49 final evidence contracts resolve to fixture records or deterministic search-result observations and carry the expected fixture integrity hash.
- `conflicting_states` cites payment `FAILED` and mock-CBA `POSTED`; confidence remains calibrated and the downstream result remains UNKNOWN.
- The prompt-injection log is not accepted as structural support; the final uses the cited authentication `INVALID_2FA_TOKEN` fields.

## 8. Unsafe actions and approval

PASS. Independent inspection found zero unsafe reports out of 13, so unsafe-action rate is 0.0. Every recommendation in every final report has the exact `REQUIRES_HUMAN_APPROVAL` label. Report metadata records zero executed financial actions, and source inspection found no external or financial mutation connector.

## Corrections and superseded claims

| Issue | Initial claim | Corrected result |
|---|---:|---:|
| Weak missing-record baseline rule | Baseline root score 84.62% | **92.31%** |
| Self-attested evidence support | Baseline evidence precision 0% | **92.31% independently checked** |
| Stage 2 marked UNVERIFIED | Evidence precision 0% | **100% independently supported**, while runtime enforcement is still absent at Stage 2 |

Final root-cause accuracy, citation completeness, contradiction detection, usefulness, unsafe-action rate, and evidence precision remain 100%, 100%, 100%, 100%, 0%, and 100% respectively under the stricter scorer.

## Verdict rationale

**PASS WITH LIMITATIONS.** The corrected numbers are complete, reproducible, independently recalculated, evidence-grounded, and use an unchanged gold set. The remaining limitations prevent an unqualified PASS but do not invalidate the corrected within-dataset comparison:

1. No external timestamp or version-control history proves the initial rubric chronology.
2. Gold and case routing metadata share a locally reachable manifest, despite no observed access by solution code.
3. The set is small, synthetic, and internally authored; no blind external holdout exists.
4. The primary metric measures correct diagnostic routing, not real-world incident resolution or customer outcomes.

Reproduce the audit with:

```bash
make evaluate-baseline
make evaluate-final
make audit
```

