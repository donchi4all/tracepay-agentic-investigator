# TracePay

TracePay is a complete, local, deterministic agent workflow for investigating failed **synthetic** payment transactions. It helps a payment operations engineer replace multi-system searching, manual timeline reconstruction, state reconciliation, and incident-report writing with one evidence-grounded command.

It is not a chatbot and it never moves money. TracePay reads only repository fixtures, treats log text as untrusted data, verifies every material conclusion, and labels every proposed follow-up `REQUIRES_HUMAN_APPROVAL`.

Judges: start with the structured [`docs/HACKATHON_REPORT.md`](docs/HACKATHON_REPORT.md). The sanitized public-clone terminal transcript is supporting appendix evidence, not the primary report.

## User, bottleneck, and value

- **User:** a payment operations engineer investigating one failed transaction at a time.
- **Bottleneck:** evidence is split across payment, authentication, approval-workflow, and downstream banking records. The operator must search, order timestamps, reconcile conflicting state, and defend the written conclusion manually.
- **Value:** one command creates a readable and machine-verifiable incident report with an ordered timeline, cited claims, contradictions, unknowns, and safely gated next steps. TracePay measures diagnostic correctness and report quality; it does **not** claim measured operator time savings or production customer outcomes.

## Measured outcome

Rubric v1.0 was declared before the initial final run; audit-corrected v1.1 was specified before the corrected rerun. The repository has no Git history to independently prove the initial chronology, which is disclosed in the audit. Baseline and final modes receive identical fixtures and local resources and do not receive gold labels.

| Frozen metric | Fair baseline | Final agent |
|---|---:|---:|
| Root-cause identification | 92.31% (12/13) | **100% (13/13)** |
| Independently checked evidence precision | 92.31% | **100%** |
| Citation completeness | 100% | **100%** |
| Contradiction detection | 0% | **100%** |
| Useful-report score | 96.92% | **100%** |
| Unsafe action rate | **0%** | **0%** |
| Median runtime on recorded clean-venv run | 0.30 ms | 0.40 ms |
| Provider cost per case | $0.00 | $0.00 |

Sources: [`evaluation/results/baseline.json`](evaluation/results/baseline.json), [`evaluation/results/final.json`](evaluation/results/final.json), and raw case-level JSONL beside each summary. Runtime is environment-dependent; cost excludes local CPU/electricity.

The highest-impact primary-metric change was structural evidence correlation (Stage 1), which moved root-cause accuracy from 92.31% to 100%. Claim verification (Stage 3) was the highest-impact enforcement change. Unconstrained hypothesis fan-out was removed after it added unsupported claims without improving accuracy.

## Audit corrections—not hidden

- The original baseline unfairly treated a zero-record lookup as an unstructured error. A generic, gold-independent absence rule corrected baseline accuracy from **84.62% (11/13)** to **92.31% (12/13)**.
- Rubric v1.0 trusted self-declared verification status when scoring evidence precision. Audit-corrected v1.1 independently checks valid evidence IDs and allow-listed structural support; corrected baseline precision is 92.31% and final precision remains 100%.
- The gold manifest did not change, but the workspace has no Git history or external timestamp that independently proves the original rubric chronology.

These are reasons for the independent verdict **PASS WITH LIMITATIONS**, not footnotes to remove. See [`evaluation/AUDIT.md`](evaluation/AUDIT.md) and [`evaluation/results/audit.json`](evaluation/results/audit.json).

## Quick start

Requirements: Python 3.9–3.12; no network, API key, package download, or paid service. Python 3.9.6 is the version recorded on the development host.

`make install` is a deterministic, pip-free local installation: it creates an isolated virtual environment and registers this repository's `src` directory with a venv-local `.pth` source link. It does not build or install a wheel. A plain import smoke test fails the target if that source registration is not usable.

```bash
make install
make validate-data
make test
make run-baseline CASE=invalid_pin
make investigate CASE=conflicting_states
make evaluate-baseline
make evaluate-final
make audit
make reproduce-all
```

Expected highlights are `case_count: 13`, `Ran 35 tests ... OK`, the focused hostile review `Ran 11 tests ... OK`, baseline root-cause score `0.9230769230769231`, final score `1.0`, audit verdict `PASS WITH LIMITATIONS`, and unsafe-action rate `0.0`. Allow approximately 1–5 seconds on a typical local host. Provider cost is $0.00.

## Baseline and agent architecture

The fair baseline receives the same sanitized fixture evidence as the final system, scans structural and free-form values with a fixed ordered keyword rule, and emits a fixed report template. It receives no gold label. This is a credible simple support script: it solves 12/13 frozen cases but misses the hostile-log case and does not reconcile contradictions.

The final workflow uses five bounded roles:

1. The coordinator publishes a fixed investigation plan.
2. The collector correlates only the selected JSON fixture, adds provenance and integrity hashes, redacts sensitive-looking values, and flags instruction-like log text.
3. The diagnostic agent orders the timeline, reconciles component state, and emits ranked hypotheses plus typed FACT, INFERENCE, and UNKNOWN claims.
4. The verifier checks citations and structural support, rejects unsupported conclusions, and lowers confidence for conflicts.
5. The reporter writes Markdown and JSON with an explicit human checkpoint.

### Why call this agentic?

TracePay is deterministic rather than LLM-driven, but it is not one opaque classification function. The coordinator owns a plan and observable state; bounded agents receive typed inputs, invoke the read-only evidence tool, produce hypotheses/claims, challenge those claims, return feedback, retry malformed evidence normalization, and stop at a human approval boundary. Separating correlation from verification was measured: correlation created the one-case accuracy gain, while verification raised contradiction detection and prevents unsupported claims from entering the accepted report.

The strongest feedback-loop example is `conflicting_states`: the reconciler emits a factual `FAILED`/`POSTED` conflict at 100% input confidence; the verifier marks it `CONFLICTED` and caps it at 65%. The overall diagnosis stays uncertain at 62%, and the reporter refuses to recommend retry or reversal. The saved trajectory records the input/output confidence and verification status without storing hidden chain-of-thought.

Try the difficult case:

```bash
make investigate CASE=conflicting_states
```

It reports `TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE` at calibrated 62% pre-verification / 62% final confidence, calls out `FAILED` versus `POSTED`, and refuses to infer a safe retry or reversal.

## Safety boundary

All evidence is authored synthetic JSON accessed through a read-only fixture adapter. There are no production endpoints, credentials, network/payment clients, or code paths for payment, retry, reversal, approval, block, customer contact, or state mutation. Free-form logs are untrusted data; diagnosis and verification use allow-listed structural fields. Every recommendation is advisory and carries `REQUIRES_HUMAN_APPROVAL`. The observed final unsafe-action rate is 0%, but the label is not a substitute for an identity-aware authorization service.

## Limitations

- The 13-case dataset is small, synthetic, and authored within this project; there is no separately authored blind holdout or production user study.
- Deterministic rules target the 11 declared failure classes and may route a novel failure to an unstructured/unknown class.
- Fixture adapters do not validate production authentication, pagination, latency, clock skew, schema drift, load, or operational UX.
- Runtime measurements are local microbenchmarks, not capacity or time-saved evidence. Only CPython 3.9.6 on macOS/arm64 was exercised in the judge-grade clean audit.
- The repository has no Git history or external timestamp proving the initial rubric chronology; this is why the evaluation audit remains `PASS WITH LIMITATIONS`.

## Project map

- `src/tracepay/`: coordinator, collector, diagnostic, verifier, safety, reporting, CLI, and baseline.
- `data/synthetic/`: read-only simulated component records.
- `evaluation/`: frozen manifest/rubric, deterministic scorer, summaries, and complete per-case output.
- `tests/`: unit, integration, end-to-end, and adversarial controls.
- `trajectories/`: observable agent instructions, actions, tool responses, feedback, retry, and checkpoint events—never hidden chain-of-thought.
- `artifacts/`: generated reports and phase acceptance evidence.
- `docs/`: architecture, decisions, security, reproduction, demo, and submission evidence.

## Scope and provenance

Everything in this repository was created for the TracePay hackathon. The initial workspace was empty and was not a Git repository. There are no external connectors, production endpoints, credentials, real account identifiers, or customer data. All project code and documentation are MIT-licensed; runtime code uses only the Python standard library.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`evaluation/RUBRIC.md`](evaluation/RUBRIC.md), and [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md) for the auditable detail.
