# Security, privacy, safety, and ethics review

## Review status

This document records the hostile review performed on 2026-08-29. Controls are not marked effective merely because they appear here: each control below identifies executable evidence in `tests/test_security_controls.py`, and the actual focused output is saved in `artifacts/phase-checks/security-review.txt`.

**Review outcome: PASS WITH RESIDUAL RISKS.** Two issues were found and corrected; no unresolved high- or medium-severity finding remains in the current local-only scope.

The review scope is `src/tracepay/`, all 13 fixtures, the case manifest, `.env.example`, dependency metadata, licences, generated reports, raw evaluation outputs, and observable trajectories. `.venv/` and Python bytecode caches are generated tooling and are excluded.

## Assets, adversaries, and trust boundaries

Protected assets are customer/payment confidentiality, authentication material, transaction integrity, operator decision quality, and the human authorization boundary. The assumed adversaries are:

- a malicious or compromised fixture record containing instruction-like text;
- an accidental contributor introducing customer data, credentials, a production endpoint, or an external connector;
- a generated report or trajectory leaking secrets or workstation identity;
- a caller attempting to turn an advisory recommendation into an automatic payment-state action;
- incomplete or conflicting downstream evidence creating false certainty;
- a dependency or licence change silently expanding the supply-chain boundary.

Trust boundaries:

```text
untrusted fixture payload
        |
        v
read-only FixtureRepository -> collector redaction/injection flagging
        |                                  |
        | structural fields only           | observable metadata only
        v                                  v
diagnostic + verifier                 trajectory recorder redaction
        |
        v
advisory report -> REQUIRES_HUMAN_APPROVAL -> external human-controlled process
```

Fixture payload is untrusted. Fixture file routing and deterministic code are inside the local test boundary. No production system, network service, model provider, or financial execution adapter is trusted or available because none is connected.

## Findings discovered and corrected

### SEC-001 — absolute workstation paths in trajectories — corrected

Severity: **Medium privacy**. Generated trajectory `tool_response` events and report metadata exposed `<HOME>/...`, revealing workstation identity and directory structure.

Correction: coordinator report paths are now repository-relative or reduced to a filename when external; reporter events persist filenames only; CLI output is relative; and `TrajectoryRecorder` independently redacts local home paths in all detail fields. The generated trajectories were regenerated. The control-specific test injects a fake macOS home path and verifies it is absent.

### SEC-002 — unpinned build-only dependency — corrected

Severity: **Low supply-chain/reproducibility**. `setuptools>=61` allowed an uncontrolled build backend version if a user chose a package-build workflow.

Correction: build metadata now pins `setuptools==68.2.2`. The judged and clean-reproduction path still installs no packages and has zero runtime dependencies.

No credential, real-customer-data, production-endpoint, external mutation, unsafe recommendation, false downstream certainty, or prompt-injection control failure was observed. This is bounded evidence from static inspection and tests, not proof against every future change.

## Control matrix

| Threat/control objective | Implemented control | Executable evidence |
|---|---|---|
| Real customer or production data | All references require `TX-SYN-*`; fixtures are local authored JSON; scanner rejects URL/production/PII patterns. | `test_01_fixtures_are_explicitly_synthetic_and_have_no_customer_or_production_data` |
| Credentials, PINs, OTPs, tokens, or accounts | Fixture-sensitive fields contain non-secret alphabetic `SYNTHETIC_*_SENTINEL` values only; there are no account-number/PAN fields; secret and long-number patterns are scanned. | `test_02_sensitive_fixture_fields_are_non_secret_sentinels_and_no_accounts_exist` |
| Fixture prompt injection | Payload is always data; collector flags instruction-like text; diagnostic and verifier read allow-listed structural fields and never free-form messages; there is no LLM prompt boundary. | `test_03_prompt_injection_log_cannot_control_final_diagnosis_or_citations` |
| Adapter mutation | `FixtureRepository` exposes lookup/load/hash operations only. Hashes of every fixture are checked before and after all 13 investigations. | `test_04_fixture_adapter_is_read_only_for_every_case` |
| Payment or state-changing execution | Runtime imports no HTTP, socket, subprocess, cloud, or payment client; no mutation call exists; reports are local files and metadata must record zero actions. | `test_05_runtime_has_no_external_or_financial_mutation_capability` |
| Sensitive output | Recursive redaction covers sensitive keys, bearer-like text, email, long numbers, and local home paths before evidence/trajectory persistence. | `test_06_sensitive_values_are_redacted_before_evidence_and_reports` |
| False certainty under timeout/conflict | Timeout and FAILED/POSTED conflict map to `TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE`, retain UNKNOWN claims, and never assert transaction success/failure as authoritative. Conflict confidence is capped at 0.65. | `test_07_ambiguous_downstream_state_is_not_forced_to_failed_or_successful` |
| Unreviewed consequential recommendation | Every recommendation and safety notice carries exact `REQUIRES_HUMAN_APPROVAL`; there is no execution callback. | `test_08_every_consequential_recommendation_requires_human_approval` |
| Undocumented dependency/licence | Project and component licences and dependency roles are enumerated below; metadata pins the only build dependency. | `test_09_dependencies_and_licences_are_declared` |
| Trajectory or shared-log leak | Recorder applies defense-in-depth redaction; shared-log sanitizers replace project, venv, and temporary roots; events store counts, IDs, class/state summaries, relative filenames, and concise rationales—not raw sensitive values or hidden reasoning. | `test_10_trajectories_and_shared_logs_redact_secrets_pii_and_local_paths` |
| Unsafe environment template | `.env.example` contains three non-secret local defaults, no secret-key variables, absolute paths, credentials, or endpoints. | `test_11_env_example_has_safe_local_defaults_and_no_secret_placeholders` |

## Data and privacy analysis

The frozen set contains 13 authored synthetic cases and 36 simulated source records. Transaction references use the `TX-SYN-` namespace. Source systems are local names (`payment_service`, `auth_service`, `approval_workflow`, `mock_cba`, and `application_log`), not endpoints.

Three sensitive-key fixture fields exist solely to exercise redaction: a PIN sentinel, OTP sentinel, and token sentinel. They are non-numeric, non-secret labels and are replaced with `[REDACTED]` before an `EvidenceItem` exists. No account number, PAN, email, customer name/ID, telephone number, private key, cloud key, bearer credential, JWT, API token, or HTTP(S) endpoint is present in fixture data.

Integrity SHA-256 hashes are provenance values, not authentication secrets. Failure-class strings such as `INVALID_PIN` and `INVALID_2FA_TOKEN` identify synthetic error categories and contain no authentication value.

## Injection analysis

`prompt_injection_log` deliberately contains a hostile free-form message. The collector detects it and records only the record ID and payload path in the trajectory security finding. The final root claim cites the structural auth record containing `INVALID_2FA_TOKEN`; it does not cite the hostile application-log record. Diagnostic code reads `error_code`, `reason_code`, `rule_code`, source, event type, and state; it never evaluates a fixture string as code or agent instruction.

The simple baseline intentionally remains vulnerable to keyword confusion and fails this case. It is not connected to an LLM or action system and cannot mutate state. The final agent path is the safety subject of this control.

## Read-only and financial safety boundary

`FixtureRepository` has no write/update/delete method. `ReportGenerator` writes only under the caller-selected local artifact directory. TracePay imports no network or financial SDK and holds no credentials or endpoints. There is no implementation for payment, retry, reversal, block, approval, customer contact, or transaction-state mutation.

Recommendations are strings in an advisory report. Even read-only reconciliation suggestions carry `REQUIRES_HUMAN_APPROVAL`. A qualified operator must move to a separate controlled system and authorization process for any real follow-up.

## Dependency and licence inventory

| Component | Version/role | Licence | Network/runtime use |
|---|---|---|---|
| TracePay source, fixtures, tests, docs | 1.0.0 | MIT (`LICENSE`) | Local only |
| CPython standard library | Supported 3.9–3.12; recorded 3.9.6 | Python Software Foundation License | Only runtime dependency; local only |
| setuptools | 68.2.2, pinned build backend metadata | MIT | Build-only; not invoked by judged or clean-reproduction commands |

No third-party runtime library, model weight, remote API, production dataset, connector, browser asset, or vendored package is included.

## Observed test results

The final observed commands and outputs are saved, not transcribed from expectation:

| Executed check | Actual result | Runtime |
|---|---:|---:|
| `make security-review` / 11 hostile control tests | **11 passed, 0 failed** | 0.044 s |
| `make test` / complete regression suite | **36 passed, 0 failed** | 0.058 s |
| `make reproduce-all` / isolated pip-free temporary venv | **PASS**, including local installation, validation, security review, evaluation, audit, reports, and eight phase checks | 2.152 s |
| Post-generation secret/endpoint/path scan over fixtures, reports, evaluation results, and trajectories | **0 real credential, sentinel leak, endpoint, private-key, or developer-home-path matches** | <0.1 s |

Data validation also reported 13 valid cases and `synthetic_only: true`. The focused suite hashes all fixture files before and after all 13 investigations and observed no mutation. These artifacts are in `artifacts/phase-checks/security-review.txt`, `tests.txt`, and `clean-reproduction.txt`.

A passing result means the listed attacks were exercised on this revision; it does not guarantee future code or untested integrations are safe.

Run directly:

```bash
make security-review
make test
```

## Ethical boundary and residual risks

TracePay is decision support, not an autonomous financial actor. It cannot establish real customer impact or authorize remediation. Ambiguity remains UNKNOWN and must not be converted into a retry or reversal.

Residual risks:

1. Static patterns cannot prove that future synthetic-looking data was not copied from a real source; provenance still requires contributor review.
2. If a future LLM or production connector is added, this threat model is invalid until the new prompt, network, authentication, and authorization boundaries are reviewed.
3. `REQUIRES_HUMAN_APPROVAL` is a report contract, not an identity-aware approval service.
4. Free-form hostile text remains present in sanitized JSON evidence for forensic fidelity, although deterministic agents do not consume it diagnostically. Any future generative component must use an isolated structured view or quarantine it.
5. Regex redaction reduces common leakage but is not a full data-loss-prevention system.
