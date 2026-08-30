# Decisions and assumptions

This log records non-blocking defaults made on 2026-08-29 before implementation.

| ID | Decision | Reason and consequence |
|---|---|---|
| D-001 | The primary user is a payment operations engineer handling one failed transaction at a time. | Keeps the command-line flow and report focused on incident triage. |
| D-002 | The judged implementation is deterministic, local-only, and has no runtime dependencies. | The available host has Python 3.9.6 and no third-party packages. The code is compatible with Python 3.9–3.12 and clean reproduction does not require network access or paid APIs. |
| D-003 | Python dataclasses and enums are the typed schema layer. | They provide explicit, validated contracts without making Pydantic or an LLM a clean-run dependency. |
| D-004 | Fixture JSON files are the only evidence adapters. | This establishes a concrete read-only trust boundary and prevents accidental production access. |
| D-005 | A transaction absent from all fixture systems is supported by a synthetic `SEARCH_RESULT` evidence item. | Even an absence claim must be citable and verifiable. |
| D-006 | The final agent uses evidence priority and state reconciliation rules frozen before final evaluation. | Determinism enables exact gold-label scoring and avoids LLM-as-judge evaluation. |
| D-007 | The fair baseline scans the same sanitized evidence bundle using keyword matching and a fixed template. | It is realistic for a simple support script, receives no gold labels, and has the same local resources. |
| D-008 | All next steps are advisory and carry `REQUIRES_HUMAN_APPROVAL`, even when read-only. | This conservative rule makes the financial safety boundary obvious to judges and operators. |
| D-009 | Runtime cost is reported as USD 0.00. | The judged path makes no API or network calls; local CPU/electricity cost is excluded and documented. |
| D-010 | The project is entirely new for this hackathon. | The inspected workspace was empty and not a Git repository; nothing is claimed as pre-existing. |
| D-011 | The primary evaluation set has 13 cases rather than the minimum 12. | This covers all requested categories and separates invalid PIN from invalid 2FA. |
| D-012 | “Useful report” is a deterministic five-point checklist. | It avoids subjective model judging while rewarding correctness, evidence, uncertainty, contradictions, and safe next steps. |

No credentials, external endpoints, customer data, or real transaction identifiers are required or permitted.

