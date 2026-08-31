# TracePay judge Q&A

## What is TracePay in one sentence?

TracePay is a local, read-only workflow that turns one synthetic failed-payment reference into a cited Markdown/JSON incident report, independently verifies each material claim, preserves uncertainty, and stops at human approval.

## Who is the user and what is the bottleneck?

A payment operations engineer. The bottleneck is reconstructing and defending one timeline from payment, authentication, approval, and downstream banking evidence—not reading one error string.

## Is this only a deterministic rules pipeline with agent names?

It is deterministic, and one static function could reproduce the same outputs. The defensible agentic contribution is the controlled separation of stateful responsibilities: a coordinator controls the sequence; a collector invokes a read-only evidence tool and normalizes/retries; a reconciler dynamically selects/ranks a diagnosis from state; a verifier can reject claims or lower confidence; and a reporter enforces a human checkpoint. Trajectories expose those state transitions without claiming hidden reasoning. The honest verdict is **DEFENSIBLY AGENTIC**, not strongly autonomous.

## What changes dynamically?

Record acceptance/fallback/skip, prompt-injection findings, failure-class selection, conflict detection, unknown creation, lower-ranked alternatives, claim acceptance/rejection, confidence caps, missing-source lists, and recommendation selection all depend on the collected investigation state.

## Where does feedback affect a later output?

In `conflicting_states`, structural verification marks the conflict claim `CONFLICTED` and changes confidence from 1.0 to 0.65 before the report is written. Unsupported or semantically unrelated claims are rejected and excluded. In `invalid_cba_response`, timestamp validation feedback causes an explicit `received_at` retry used in the later timeline.

## What is the live-demo moment?

Run:

```bash
make investigate CASE=conflicting_states
```

Show payment `FAILED`, mock-CBA `POSTED`, the 0.62 unknown-downstream assessment, the verifier's 1.0→0.65 conflict feedback, and the refusal to recommend retry or reversal.

## What was actually measured?

On the same 13 internally authored synthetic cases, the corrected fair baseline scores 12/13 and final scores 13/13 on exact root-cause class. Final cited structural evidence supports 14/14 material claims, 17/17 claims have valid citations, the single contradiction case is detected, and all recommendations require human approval. These are within-dataset results—not production outcomes or proof of generalization.

## Why does the baseline score 12/13?

It is a credible first-match keyword/template script using the same sanitized evidence. A post-audit generic zero-record rule fairly handles `NOT_EXIST`. It fails only `prompt_injection_log`, where hostile free-form text contains the baseline's first-priority `NO_ACTION_REQUIRED` keyword before structural `INVALID_2FA_TOKEN` evidence is considered.

## Was the baseline changed after seeing results?

Yes, transparently. The original 11/13 baseline mishandled an empty lookup. The correction was a general zero-record rule that does not read gold; the gold manifest hash remained unchanged. The repository cannot externally prove the full original rubric chronology, so that remains a limitation.

## Can the evaluation be trusted?

The raw JSONL contains every manifest case exactly once. A clean rerun reproduced all aggregates. A separate one-off audit that imported no TracePay/evaluation module again checked identities, cited structural support, citation resolution, exact conflict evidence, usefulness points, approval labels, runtimes, fixture integrity, and baseline/final evidence equality. Results match. The important limitation is external validity: the corpus is small, same-authored, and not blind.

## Are the perfect secondary scores too easy?

They are correct on the current final outputs but narrow: 14 material claims, 17 total claims, and one contradiction-eligible case. The scorer also assigns 1.0 to zero denominators, so claim omission could game citation/evidence metrics. Final does not use a zero denominator, but judges should treat these as corpus-specific checks, not broad production proof.

## Does evidence precision trust the report's own verification label?

No in rubric v1.1. Credit requires that cited allow-listed structural source/state/code fields independently support the statement. A valid ID attached to an unrelated claim is rejected by both the runtime verifier and scorer tests.

## What is the highest-impact change?

Structural correlation and prioritizing allow-listed fields over free-form logs moved exact root-cause accuracy from 12/13 to 13/13. Verification was the highest-impact enforcement change: it raised contradiction detection from 0/1 to 1/1 and blocks unsupported accepted claims.

## Why was an experiment removed?

Unconstrained fan-out kept primary accuracy at 100% but reduced evidence precision to 26.42%, citation completeness to 30.36%, and usefulness to 80%. It was removed because plausible extra text degraded trust without improving diagnosis.

## What is the hot take?

An agent system should be rewarded for deleting unsupported possibilities. Here, correlation created the routing gain; verification and removal created trust.

## Can TracePay move money or mutate a transaction?

No. Runtime source has no network/payment client, financial-action method, or fixture write/update/delete method. Attempts to call `retry`, `execute-payment`, or `reverse` are rejected by the CLI. Fresh probes observed zero fixture mutations and zero financial actions. Every recommendation is labelled `REQUIRES_HUMAN_APPROVAL`.

## Is the approval gate production authorization?

No. It is an enforced report/software contract and there is no action callback. It is not an identity-aware organizational authorization service.

## Is the project reproducible offline?

Yes for the declared synthetic mode. On CPython 3.9.6/macOS arm64, a source-only `env -i` copy installed without pip or downloads, passed 35 tests and 11 focused security tests, evaluated six modes, audited metrics, regenerated reports/trajectories, and passed eight phases in 2.23 seconds outer wall time.

## Why are runtimes sub-millisecond?

They measure only local deterministic fixture/rule/report-object processing with `time.perf_counter`. They exclude production I/O, network/storage latency, operator time, and capacity. They are not evidence of real incident-resolution speed.

## What is the strongest limitation?

There is no independently authored blind holdout. The 13 cases, expected classes, diagnostic rules, and evaluation were created in the same project, so 13/13 does not establish generalization.

## What should the presenter never claim?

Do not claim production readiness, measured time savings, customer impact, broad generalization, autonomous financial action, superiority to unseen projects, or that perfect synthetic scores mean zero real-world error.

## What should be improved next?

Use an independently authored frozen holdout with more conflict cases, novel schemas, prompt-injection variations, semantic citation-laundering, and empty-claim scorer tests. Do not add an LLM merely for appearance.

## What is the verified score and verdict?

**87/100 — READY WITH LIMITATIONS.** Technical submission blockers are absent. Human publication steps—commit/push, video recording/upload, logged-out link verification, and portal submission—remain, so the final recommendation is **FIX FIRST**.
