# Architecture

## Product boundary

TracePay investigates a single synthetic transaction reference and returns a read-only incident report. Its primary user is a payment operations engineer. Today that user would search separate payment, authentication, workflow, and core-banking records, manually align timestamps, reconcile conflicting states, and write a report. The bottleneck is evidence correlation and defensible synthesis, not payment execution.

The exact product output is a Markdown report plus a machine-readable JSON report. Both contain a ranked root-cause assessment, evidence-linked claims, contradictions, unknowns, and advisory next steps guarded by a human approval checkpoint.

## Components

```text
transaction reference
        |
   Coordinator -----> observable JSONL trajectory
        |
 Evidence Collector ---- read-only JSON fixture repository
        |
 State Reconciler / Diagnostic Agent
        |
 Verification Agent
        |
 Report Generator -----> Markdown + JSON
```

- **Coordinator:** validates the case, publishes the investigation plan, invokes each component in a controlled sequence, and owns observable state.
- **Evidence Collector:** searches only `data/synthetic`, correlates by transaction reference, normalizes timestamps, redacts sensitive-looking content, and creates an integrity hash for every evidence item.
- **State Reconciler / Diagnostic Agent:** orders evidence, compares system states, and produces a ranked primary failure class plus structured FACT, INFERENCE, or UNKNOWN claims.
- **Verification Agent:** confirms cited evidence exists, rejects unsupported claims, identifies contradictions, and calibrates confidence.
- **Report Generator:** renders professional Markdown and JSON, with evidence citations and approval-labelled recommendations.

Fixture content is data, never executable instructions. The collector may flag prompt-injection language for audit, but downstream logic only consumes allow-listed structural fields such as event type, state, error code, and reason code.

## Scope and non-goals

In scope: synthetic incident investigation, reproducible evaluation, evidence redaction, contradiction handling, and report generation. Out of scope: real connectors, payment execution, retry/reversal/block/approval operations, production monitoring, customer messaging, and autonomous remediation.

## Acceptance criteria

1. All 13 fixtures pass privacy and schema validation.
2. Baseline and final modes run on exactly the same case files.
3. Every material final claim has the required structured claim contract and existing evidence identifiers.
4. The final evaluation improves root-cause identification over the fair baseline.
5. Unsafe action rate is 0%, all tests pass, and no code path mutates fixture state.
6. A clean local command reproduces validation, tests, experiments, reports, metrics, trajectories, and phase checks.

## Requirement-to-evidence matrix

| Requirement | Deliverable | Verification command |
|---|---|---|
| Named user, bottleneck, value | `README.md`, this document | `make phase-checks` |
| Fair baseline and agent | `baseline/`, `src/tracepay/` | `make evaluate-baseline evaluate-final` |
| Same cases/resources | `evaluation/run_evaluation.py` | `make test` |
| Frozen predeclared rubric | `evaluation/RUBRIC.md` | `make validate-data` |
| At least 10 diverse cases | 13 case and fixture files | `make validate-data` |
| Meaningful experiments and removal | `CHANGELOG.md`, stage results | `make evaluate-all` |
| Claims linked to evidence | result JSON, reports | `make phase-checks` |
| Exact clean reproduction | `docs/REPRODUCTION.md`, script | `make reproduce-all` |
| Observable trajectories | `trajectories/*.jsonl` | `make investigate` |
| Synthetic data only | fixtures and validator | `make validate-data` |
| Local simulations only | fixture repository | `make test` |
| No financial actions | safety module and tests | `make test` |
| New vs pre-existing | `docs/DECISIONS.md` D-010 | `make phase-checks` |
| Licences documented | `LICENSE`, `docs/SECURITY_AND_ETHICS.md` | `make phase-checks` |

