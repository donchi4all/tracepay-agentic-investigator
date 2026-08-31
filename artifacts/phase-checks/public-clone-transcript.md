# Sanitized public-clone terminal evidence

This appendix is supporting execution evidence, not the primary hackathon report. It was captured after cloning the public repository and then sanitized mechanically. User/host identity, repository paths, virtual-environment paths, and temporary directories are replaced with explicit placeholders.

## Runtime provenance

The standalone `make evaluate-baseline` / `make evaluate-final` commands in this transcript measured **0.424042 ms / 0.453333 ms** median runtime. The later isolated `make reproduce-all` run measured **0.302250 ms / 0.387834 ms** and rewrote that clone's saved result files. Both runs have identical qualitative metrics. Runtime is environment-dependent, so these pairs must not be mixed in one results table.

The authoritative primary report uses whichever baseline/final summaries and raw JSONL files are currently saved together in `evaluation/results/`.

<details>
<summary>Show sanitized transcript</summary>

```text
<USER>@<HOST> <REPOSITORY> % make install
python3 -m venv --without-pip .venv
.venv/bin/python scripts/install_local.py
Installed TracePay source link: <VIRTUAL_ENV>/lib/python3.9/site-packages/tracepay-local.pth
Runtime dependencies installed: 0
.venv/bin/python -c "import tracepay, sys; print('TracePay', tracepay.__version__, 'installed on Python', sys.version.split()[0])"
TracePay 1.0.0 installed on Python 3.9.6
<USER>@<HOST> <REPOSITORY> % make validate-data
.venv/bin/python -m tracepay validate-data
{
  "case_count": 13,
  "categories_present": [
    "adversarial",
    "approver_amount_limit",
    "conflicting_evidence",
    "difficult",
    "duplicate_request",
    "edge_case",
    "empty_error_with_context",
    "initiator_amount_limit",
    "initiator_count_limit",
    "invalid_cba_response",
    "malformed_timestamp",
    "missing_transaction",
    "no_action_required_already_final",
    "normal",
    "prompt_injection_in_log",
    "retry_correction",
    "straightforward_authentication_failure",
    "timeout_ambiguous_downstream"
  ],
  "errors": [],
  "failure_classes_present": [
    "DUPLICATE_OR_ALREADY_PROCESSED_REQUEST",
    "EMPTY_OR_UNSTRUCTURED_ERROR",
    "FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED",
    "FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED",
    "FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED",
    "INVALID_2FA_TOKEN",
    "INVALID_CBA_RESPONSE_DATA",
    "INVALID_PIN",
    "NOT_EXIST",
    "NO_ACTION_REQUIRED",
    "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE"
  ],
  "fixture_hashes": {
    "already_final": "sha256:c5d64828ce34af6a6163c6590d2c841f8ef8de6eac6b00bc12a4dbbe0fe8f542",
    "approver_amount_limit": "sha256:afed2b66263602e15529733ef46667d8a33fad0db837c881b377b997971c4917",
    "conflicting_states": "sha256:e3d1ccccd8dbbfce8768bec6173cdf49bdfa4fc1b680b1c3ff312ec2700883af",
    "duplicate_request": "sha256:40785adbae979abf9f2b8cfdff9435a9299fa09dbe85f9f645021a61ec94b33b",
    "empty_error_context": "sha256:48d51ea1cc1bdbb436b3c59f36c575d1b4f4c2e92c6b39fff63aeca8385a1faa",
    "initiator_amount_limit": "sha256:63711e156f44d18ed0f0e05adddc2984ea04500a5720ed1cd7911d1afcdacaa3",
    "initiator_count_limit": "sha256:032889aa6f10069a5af0afbe377f1139a7788621e1efaef8b40d24732f94bc76",
    "invalid_2fa": "sha256:dd4c4b56457a96ca494fd724f7c83072b230f9d3a29a9f6a82c748e667e365d2",
    "invalid_cba_response": "sha256:b6cc5aaeae026b000dc68b3705467a3b1a78753a44a9e84fea04bec3a71239bf",
    "invalid_pin": "sha256:efad3e96cf477607aca88b06bf7ea6c6534cd8240fe6b29418c66c5b630645ad",
    "missing_transaction": "sha256:899eca28a8ecf2c3ebb13523eae5381bccfdc961ecfce20abf6ada4d333cc431",
    "prompt_injection_log": "sha256:6ee7be7ab252e2e8c8d6b5ded44c11c9d914eef602610393e76ffe030f93dbd1",
    "timeout_ambiguous": "sha256:f6b18699e937c782a84e6f6232923d03e28ba1164f394f583cae2416f6e23a8b"
  },
  "synthetic_only": true,
  "valid": true
}
<USER>@<HOST> <REPOSITORY> % make test
.venv/bin/python scripts/run_tests.py
$ <VIRTUAL_ENV>/bin/python -m unittest discover -s tests -v
test_evidence_contract_and_fixture_are_read_only (test_collector.CollectorTests) ... ok
test_hostile_log_is_flagged (test_collector.CollectorTests) ... ok
test_malformed_record_without_fallback_is_skipped_not_invented (test_collector.CollectorTests) ... ok
test_malformed_timestamp_uses_explicit_fallback_and_records_retry (test_collector.CollectorTests) ... ok
test_conflicting_states_are_not_forced_to_false_certainty (test_diagnostic.DiagnosticTests) ... ok
test_duplicate_events_remain_distinct_evidence (test_diagnostic.DiagnosticTests) ... ok
test_empty_error_preserves_unknown (test_diagnostic.DiagnosticTests) ... ok
test_missing_transaction_uses_search_evidence (test_diagnostic.DiagnosticTests) ... ok
test_all_gold_classes_and_claim_contracts (test_end_to_end.EndToEndTests) ... ok
test_prompt_injection_cannot_override_structural_auth_code (test_end_to_end.EndToEndTests) ... ok
test_report_writes_markdown_json_and_observable_agents (test_end_to_end.EndToEndTests) ... ok
test_timeline_is_sorted_despite_conflicting_source_order (test_end_to_end.EndToEndTests) ... ok
test_evidence_support_is_independent_of_self_reported_status (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_fair_baseline_handles_zero_record_lookup (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_free_form_injection_text_is_not_structural_support (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_invalid_ids_and_generic_contradiction_do_not_receive_credit (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_prompt_injection_is_flagged_as_data (test_safety.SafetyTests) ... ok
test_sensitive_keys_and_patterns_are_redacted (test_safety.SafetyTests) ... ok
test_unsafe_requested_action_requires_label (test_safety.SafetyTests) ... ok
test_01_fixtures_are_explicitly_synthetic_and_have_no_customer_or_production_data (test_security_controls.SecurityControlTests) ... ok
test_02_sensitive_fixture_fields_are_non_secret_sentinels_and_no_accounts_exist (test_security_controls.SecurityControlTests) ... ok
test_03_prompt_injection_log_cannot_control_final_diagnosis_or_citations (test_security_controls.SecurityControlTests) ... ok
test_04_fixture_adapter_is_read_only_for_every_case (test_security_controls.SecurityControlTests) ... ok
test_05_runtime_has_no_external_or_financial_mutation_capability (test_security_controls.SecurityControlTests) ... ok
test_06_sensitive_values_are_redacted_before_evidence_and_reports (test_security_controls.SecurityControlTests) ... ok
test_07_ambiguous_downstream_state_is_not_forced_to_failed_or_successful (test_security_controls.SecurityControlTests) ... ok
test_08_every_consequential_recommendation_requires_human_approval (test_security_controls.SecurityControlTests) ... ok
test_09_dependencies_and_licences_are_declared (test_security_controls.SecurityControlTests) ... ok
test_10_trajectories_redact_secrets_pii_log_text_and_local_paths (test_security_controls.SecurityControlTests) ... ok
test_11_env_example_has_safe_local_defaults_and_no_secret_placeholders (test_security_controls.SecurityControlTests) ... ok
test_baseline_is_functional_and_safe (test_validation_and_baseline.ValidationAndBaselineTests) ... ok
test_dataset_is_frozen_diverse_and_synthetic (test_validation_and_baseline.ValidationAndBaselineTests) ... ok
test_gold_labels_are_not_present_in_baseline_input (test_validation_and_baseline.ValidationAndBaselineTests) ... ok
test_missing_citation_is_rejected (test_verifier.VerifierTests) ... ok
test_semantically_unsupported_claim_is_rejected_even_with_valid_id (test_verifier.VerifierTests) ... ok

----------------------------------------------------------------------
Ran 35 tests in 0.062s

OK
<USER>@<HOST> <REPOSITORY> % make run-baseline CASE=invalid_pin

.venv/bin/python -m tracepay baseline invalid_pin
baseline case=invalid_pin class=INVALID_PIN report=artifacts/reports/baseline_invalid_pin.json
<USER>@<HOST> <REPOSITORY> % make investigate CASE=conflicting_states

.venv/bin/python -m tracepay investigate conflicting_states
investigation case=conflicting_states class=TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE confidence=0.62 markdown=artifacts/reports/conflicting_states.md json=artifacts/reports/conflicting_states.json
<USER>@<HOST> <REPOSITORY> % make evaluate-baseline

.venv/bin/python evaluation/run_evaluation.py --mode baseline
{
  "case_count": 13,
  "citation_completeness": 1.0,
  "contradiction_detection_rate": 0.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 0.9230769230769231,
  "executed_at": "2026-08-30T10:20:19.877549Z",
  "median_runtime_ms": 0.4240419999999995,
  "mode": "baseline",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 0.9230769230769231,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 0.9692307692307692
}
<USER>@<HOST> <REPOSITORY> % make evaluate-final

.venv/bin/python evaluation/run_evaluation.py --mode final
{
  "case_count": 13,
  "citation_completeness": 1.0,
  "contradiction_detection_rate": 1.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 1.0,
  "executed_at": "2026-08-30T10:20:28.054659Z",
  "median_runtime_ms": 0.4533330000000002,
  "mode": "final",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 1.0,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 1.0
}
<USER>@<HOST> <REPOSITORY> % make audit

.venv/bin/python evaluation/run_audit.py
{
  "all_recomputed_metrics_match": true,
  "audited_at": "2026-08-30T10:20:34.488699Z",
  "claim_and_citation_audit": {
    "final_all_claims": 17,
    "final_material_claims": 14,
    "final_supported_material_claims": 14,
    "final_validly_cited_claims": 17,
    "fixture_contracts": {
      "evidence_contracts_checked": 49,
      "failures": [],
      "passed": true
    }
  },
  "corrections": [
    {
      "corrected_baseline_root_score": 0.9230769230769231,
      "finding": "The initial baseline failed an empty repository lookup instead of returning NOT_EXIST.",
      "id": "AUD-001",
      "old_baseline_root_score": 0.8461538461538461,
      "resolution": "Added a generic zero-record rule before keyword matching; no gold label is read."
    },
    {
      "corrected_baseline_evidence_precision": 0.9230769230769231,
      "finding": "The initial evidence-precision scorer trusted self-declared verification status and did not independently establish semantic support.",
      "id": "AUD-002",
      "old_baseline_evidence_precision": 0.0,
      "resolution": "Version 1.1 independently checks cited structural fields, valid IDs, and exact conflict state before credit."
    }
  ],
  "coverage_and_fairness": {
    "baseline_failures": [
      "prompt_injection_log"
    ],
    "baseline_reasonable_after_correction": true,
    "difficult_cases": [
      "timeout_ambiguous",
      "conflicting_states"
    ],
    "gold_present_in_fixture_files": false,
    "raw_case_sets_exactly_match_manifest": true,
    "required_categories_present": true,
    "same_sanitized_evidence_per_case": true,
    "solution_source_gold_references": []
  },
  "evidence": {
    "audit_implementation": "evaluation/run_audit.py",
    "baseline_raw": "evaluation/results/baseline_raw.jsonl",
    "final_raw": "evaluation/results/final_raw.jsonl",
    "manifest": "evaluation/cases/manifest.json",
    "rubric": "evaluation/RUBRIC.md"
  },
  "gold_manifest": {
    "case_count": 13,
    "expected_pre_correction_sha256": "66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1",
    "sha256": "66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1",
    "unchanged": true
  },
  "limitations": [
    "The initial v1.0 rubric's pre-final chronology cannot be independently proven without Git history or an external timestamp.",
    "Gold labels share a manifest file reachable from the local repository layer, although static inspection found no gold reference in solution code and gold is absent from fixtures.",
    "The 13-case dataset is synthetic, small, and authored in the same project; a separately authored blind holdout is still needed for generalization claims.",
    "The primary metric captures diagnostic routing value but not real production resolution time or customer outcome."
  ],
  "metric_matches": {
    "baseline": {
      "case_count": true,
      "citation_completeness": true,
      "contradiction_detection_rate": true,
      "estimated_cost_usd_per_case": true,
      "evidence_precision": true,
      "median_runtime_ms": true,
      "root_cause_identification_score": true,
      "unsafe_action_rate": true,
      "useful_report_score": true
    },
    "final": {
      "case_count": true,
      "citation_completeness": true,
      "contradiction_detection_rate": true,
      "estimated_cost_usd_per_case": true,
      "evidence_precision": true,
      "median_runtime_ms": true,
      "root_cause_identification_score": true,
      "unsafe_action_rate": true,
      "useful_report_score": true
    }
  },
  "primary_metric_value": {
    "finding": "Exact failure-class identification directly measures whether an operator is routed to the correct diagnosis; evidence, safety, conflict, and usefulness are covered by secondary metrics.",
    "status": "PASS"
  },
  "published_metrics": {
    "baseline": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 0.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 0.9230769230769231,
      "median_runtime_ms": 0.4240419999999995,
      "root_cause_identification_score": 0.9230769230769231,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 0.9692307692307692
    },
    "final": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 1.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 1.0,
      "median_runtime_ms": 0.4533330000000002,
      "root_cause_identification_score": 1.0,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 1.0
    }
  },
  "recomputed_metrics": {
    "baseline": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 0.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 0.9230769230769231,
      "median_runtime_ms": 0.4240419999999995,
      "root_cause_identification_score": 0.9230769230769231,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 0.9692307692307692
    },
    "final": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 1.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 1.0,
      "median_runtime_ms": 0.4533330000000002,
      "root_cause_identification_score": 1.0,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 1.0
    }
  },
  "rubric": {
    "chronology_independently_verifiable": false,
    "corrected_v1_1_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
    "declared_pre_final_v1_0": true,
    "initial_v1_0_sha256": "02363a352a00f5145598ffc99c8dfca2404da10f424b6a262dbe8727d0abf69b",
    "published_results_use_corrected_hash": true,
    "reason": "The workspace was created without Git history; only the declaration and hashes remain."
  },
  "safety_audit": {
    "all_recommendations_human_approval_labelled": true,
    "final_unsafe_reports": 0,
    "financial_actions_executed": 0,
    "unsafe_action_rate": 0.0
  },
  "schema_version": "1.0",
  "verdict": "PASS WITH LIMITATIONS"
}
<USER>@<HOST> <REPOSITORY> % make reproduce-all

.venv/bin/python scripts/reproduce_all.py
$ <TEMP_DIR>/venv/bin/python scripts/install_local.py
Installed TracePay source link: <TEMP_DIR>/venv/lib/python3.9/site-packages/tracepay-local.pth
Runtime dependencies installed: 0
$ <TEMP_DIR>/venv/bin/python -m tracepay validate-data
{
  "case_count": 13,
  "categories_present": [
    "adversarial",
    "approver_amount_limit",
    "conflicting_evidence",
    "difficult",
    "duplicate_request",
    "edge_case",
    "empty_error_with_context",
    "initiator_amount_limit",
    "initiator_count_limit",
    "invalid_cba_response",
    "malformed_timestamp",
    "missing_transaction",
    "no_action_required_already_final",
    "normal",
    "prompt_injection_in_log",
    "retry_correction",
    "straightforward_authentication_failure",
    "timeout_ambiguous_downstream"
  ],
  "errors": [],
  "failure_classes_present": [
    "DUPLICATE_OR_ALREADY_PROCESSED_REQUEST",
    "EMPTY_OR_UNSTRUCTURED_ERROR",
    "FIRST_TIME_APPROVER_AMOUNT_LIMIT_EXCEEDED",
    "FIRST_TIME_INITIATOR_AMOUNT_LIMIT_EXCEEDED",
    "FIRST_TIME_INITIATOR_COUNT_LIMIT_EXCEEDED",
    "INVALID_2FA_TOKEN",
    "INVALID_CBA_RESPONSE_DATA",
    "INVALID_PIN",
    "NOT_EXIST",
    "NO_ACTION_REQUIRED",
    "TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE"
  ],
  "fixture_hashes": {
    "already_final": "sha256:c5d64828ce34af6a6163c6590d2c841f8ef8de6eac6b00bc12a4dbbe0fe8f542",
    "approver_amount_limit": "sha256:afed2b66263602e15529733ef46667d8a33fad0db837c881b377b997971c4917",
    "conflicting_states": "sha256:e3d1ccccd8dbbfce8768bec6173cdf49bdfa4fc1b680b1c3ff312ec2700883af",
    "duplicate_request": "sha256:40785adbae979abf9f2b8cfdff9435a9299fa09dbe85f9f645021a61ec94b33b",
    "empty_error_context": "sha256:48d51ea1cc1bdbb436b3c59f36c575d1b4f4c2e92c6b39fff63aeca8385a1faa",
    "initiator_amount_limit": "sha256:63711e156f44d18ed0f0e05adddc2984ea04500a5720ed1cd7911d1afcdacaa3",
    "initiator_count_limit": "sha256:032889aa6f10069a5af0afbe377f1139a7788621e1efaef8b40d24732f94bc76",
    "invalid_2fa": "sha256:dd4c4b56457a96ca494fd724f7c83072b230f9d3a29a9f6a82c748e667e365d2",
    "invalid_cba_response": "sha256:b6cc5aaeae026b000dc68b3705467a3b1a78753a44a9e84fea04bec3a71239bf",
    "invalid_pin": "sha256:efad3e96cf477607aca88b06bf7ea6c6534cd8240fe6b29418c66c5b630645ad",
    "missing_transaction": "sha256:899eca28a8ecf2c3ebb13523eae5381bccfdc961ecfce20abf6ada4d333cc431",
    "prompt_injection_log": "sha256:6ee7be7ab252e2e8c8d6b5ded44c11c9d914eef602610393e76ffe030f93dbd1",
    "timeout_ambiguous": "sha256:f6b18699e937c782a84e6f6232923d03e28ba1164f394f583cae2416f6e23a8b"
  },
  "synthetic_only": true,
  "valid": true
}
$ <TEMP_DIR>/venv/bin/python scripts/run_tests.py
$ <TEMP_DIR>/venv/bin/python -m unittest discover -s tests -v
test_evidence_contract_and_fixture_are_read_only (test_collector.CollectorTests) ... ok
test_hostile_log_is_flagged (test_collector.CollectorTests) ... ok
test_malformed_record_without_fallback_is_skipped_not_invented (test_collector.CollectorTests) ... ok
test_malformed_timestamp_uses_explicit_fallback_and_records_retry (test_collector.CollectorTests) ... ok
test_conflicting_states_are_not_forced_to_false_certainty (test_diagnostic.DiagnosticTests) ... ok
test_duplicate_events_remain_distinct_evidence (test_diagnostic.DiagnosticTests) ... ok
test_empty_error_preserves_unknown (test_diagnostic.DiagnosticTests) ... ok
test_missing_transaction_uses_search_evidence (test_diagnostic.DiagnosticTests) ... ok
test_all_gold_classes_and_claim_contracts (test_end_to_end.EndToEndTests) ... ok
test_prompt_injection_cannot_override_structural_auth_code (test_end_to_end.EndToEndTests) ... ok
test_report_writes_markdown_json_and_observable_agents (test_end_to_end.EndToEndTests) ... ok
test_timeline_is_sorted_despite_conflicting_source_order (test_end_to_end.EndToEndTests) ... ok
test_evidence_support_is_independent_of_self_reported_status (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_fair_baseline_handles_zero_record_lookup (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_free_form_injection_text_is_not_structural_support (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_invalid_ids_and_generic_contradiction_do_not_receive_credit (test_evaluation_scoring.EvaluationScoringTests) ... ok
test_prompt_injection_is_flagged_as_data (test_safety.SafetyTests) ... ok
test_sensitive_keys_and_patterns_are_redacted (test_safety.SafetyTests) ... ok
test_unsafe_requested_action_requires_label (test_safety.SafetyTests) ... ok
test_01_fixtures_are_explicitly_synthetic_and_have_no_customer_or_production_data (test_security_controls.SecurityControlTests) ... ok
test_02_sensitive_fixture_fields_are_non_secret_sentinels_and_no_accounts_exist (test_security_controls.SecurityControlTests) ... ok
test_03_prompt_injection_log_cannot_control_final_diagnosis_or_citations (test_security_controls.SecurityControlTests) ... ok
test_04_fixture_adapter_is_read_only_for_every_case (test_security_controls.SecurityControlTests) ... ok
test_05_runtime_has_no_external_or_financial_mutation_capability (test_security_controls.SecurityControlTests) ... ok
test_06_sensitive_values_are_redacted_before_evidence_and_reports (test_security_controls.SecurityControlTests) ... ok
test_07_ambiguous_downstream_state_is_not_forced_to_failed_or_successful (test_security_controls.SecurityControlTests) ... ok
test_08_every_consequential_recommendation_requires_human_approval (test_security_controls.SecurityControlTests) ... ok
test_09_dependencies_and_licences_are_declared (test_security_controls.SecurityControlTests) ... ok
test_10_trajectories_redact_secrets_pii_log_text_and_local_paths (test_security_controls.SecurityControlTests) ... ok
test_11_env_example_has_safe_local_defaults_and_no_secret_placeholders (test_security_controls.SecurityControlTests) ... ok
test_baseline_is_functional_and_safe (test_validation_and_baseline.ValidationAndBaselineTests) ... ok
test_dataset_is_frozen_diverse_and_synthetic (test_validation_and_baseline.ValidationAndBaselineTests) ... ok
test_gold_labels_are_not_present_in_baseline_input (test_validation_and_baseline.ValidationAndBaselineTests) ... ok
test_missing_citation_is_rejected (test_verifier.VerifierTests) ... ok
test_semantically_unsupported_claim_is_rejected_even_with_valid_id (test_verifier.VerifierTests) ... ok

----------------------------------------------------------------------
Ran 35 tests in 0.059s

OK
$ <TEMP_DIR>/venv/bin/python scripts/run_security_review.py
$ <TEMP_DIR>/venv/bin/python -m unittest tests.test_security_controls -v
test_01_fixtures_are_explicitly_synthetic_and_have_no_customer_or_production_data (tests.test_security_controls.SecurityControlTests) ... ok
test_02_sensitive_fixture_fields_are_non_secret_sentinels_and_no_accounts_exist (tests.test_security_controls.SecurityControlTests) ... ok
test_03_prompt_injection_log_cannot_control_final_diagnosis_or_citations (tests.test_security_controls.SecurityControlTests) ... ok
test_04_fixture_adapter_is_read_only_for_every_case (tests.test_security_controls.SecurityControlTests) ... ok
test_05_runtime_has_no_external_or_financial_mutation_capability (tests.test_security_controls.SecurityControlTests) ... ok
test_06_sensitive_values_are_redacted_before_evidence_and_reports (tests.test_security_controls.SecurityControlTests) ... ok
test_07_ambiguous_downstream_state_is_not_forced_to_failed_or_successful (tests.test_security_controls.SecurityControlTests) ... ok
test_08_every_consequential_recommendation_requires_human_approval (tests.test_security_controls.SecurityControlTests) ... ok
test_09_dependencies_and_licences_are_declared (tests.test_security_controls.SecurityControlTests) ... ok
test_10_trajectories_redact_secrets_pii_log_text_and_local_paths (tests.test_security_controls.SecurityControlTests) ... ok
test_11_env_example_has_safe_local_defaults_and_no_secret_placeholders (tests.test_security_controls.SecurityControlTests) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.044s

OK
$ <TEMP_DIR>/venv/bin/python evaluation/run_evaluation.py --mode baseline
{
  "case_count": 13,
  "citation_completeness": 1.0,
  "contradiction_detection_rate": 0.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 0.9230769230769231,
  "executed_at": "2026-08-30T10:20:42.229605Z",
  "median_runtime_ms": 0.3022500000000039,
  "mode": "baseline",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 0.9230769230769231,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 0.9692307692307692
}
$ <TEMP_DIR>/venv/bin/python evaluation/run_evaluation.py --mode stage1
{
  "case_count": 13,
  "citation_completeness": 0.0,
  "contradiction_detection_rate": 0.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 0.0,
  "executed_at": "2026-08-30T10:20:42.351177Z",
  "median_runtime_ms": 0.39941599999999966,
  "mode": "stage1",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 1.0,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 0.7846153846153846
}
$ <TEMP_DIR>/venv/bin/python evaluation/run_evaluation.py --mode stage2
{
  "case_count": 13,
  "citation_completeness": 1.0,
  "contradiction_detection_rate": 0.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 1.0,
  "executed_at": "2026-08-30T10:20:42.476538Z",
  "median_runtime_ms": 0.39254099999999625,
  "mode": "stage2",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 1.0,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 0.9846153846153847
}
$ <TEMP_DIR>/venv/bin/python evaluation/run_evaluation.py --mode stage3
{
  "case_count": 13,
  "citation_completeness": 1.0,
  "contradiction_detection_rate": 1.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 1.0,
  "executed_at": "2026-08-30T10:20:42.600344Z",
  "median_runtime_ms": 0.4063750000000005,
  "mode": "stage3",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 1.0,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 1.0
}
$ <TEMP_DIR>/venv/bin/python evaluation/run_evaluation.py --mode stage4_removed
{
  "case_count": 13,
  "citation_completeness": 0.30357142857142855,
  "contradiction_detection_rate": 1.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 0.2641509433962264,
  "executed_at": "2026-08-30T10:20:42.722096Z",
  "median_runtime_ms": 0.43687499999998936,
  "mode": "stage4_removed",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 1.0,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 0.8
}
$ <TEMP_DIR>/venv/bin/python evaluation/run_evaluation.py --mode final
{
  "case_count": 13,
  "citation_completeness": 1.0,
  "contradiction_detection_rate": 1.0,
  "estimated_cost_usd_per_case": 0.0,
  "evidence_precision": 1.0,
  "executed_at": "2026-08-30T10:20:42.845580Z",
  "median_runtime_ms": 0.38783400000000356,
  "mode": "final",
  "resource_note": "Local standard-library Python only; no network or paid provider calls.",
  "root_cause_identification_score": 1.0,
  "rubric_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
  "rubric_version": "1.1-audit-corrected",
  "unsafe_action_rate": 0.0,
  "useful_report_score": 1.0
}
$ <TEMP_DIR>/venv/bin/python evaluation/run_audit.py
{
  "all_recomputed_metrics_match": true,
  "audited_at": "2026-08-30T10:20:42.924751Z",
  "claim_and_citation_audit": {
    "final_all_claims": 17,
    "final_material_claims": 14,
    "final_supported_material_claims": 14,
    "final_validly_cited_claims": 17,
    "fixture_contracts": {
      "evidence_contracts_checked": 49,
      "failures": [],
      "passed": true
    }
  },
  "corrections": [
    {
      "corrected_baseline_root_score": 0.9230769230769231,
      "finding": "The initial baseline failed an empty repository lookup instead of returning NOT_EXIST.",
      "id": "AUD-001",
      "old_baseline_root_score": 0.8461538461538461,
      "resolution": "Added a generic zero-record rule before keyword matching; no gold label is read."
    },
    {
      "corrected_baseline_evidence_precision": 0.9230769230769231,
      "finding": "The initial evidence-precision scorer trusted self-declared verification status and did not independently establish semantic support.",
      "id": "AUD-002",
      "old_baseline_evidence_precision": 0.0,
      "resolution": "Version 1.1 independently checks cited structural fields, valid IDs, and exact conflict state before credit."
    }
  ],
  "coverage_and_fairness": {
    "baseline_failures": [
      "prompt_injection_log"
    ],
    "baseline_reasonable_after_correction": true,
    "difficult_cases": [
      "timeout_ambiguous",
      "conflicting_states"
    ],
    "gold_present_in_fixture_files": false,
    "raw_case_sets_exactly_match_manifest": true,
    "required_categories_present": true,
    "same_sanitized_evidence_per_case": true,
    "solution_source_gold_references": []
  },
  "evidence": {
    "audit_implementation": "evaluation/run_audit.py",
    "baseline_raw": "evaluation/results/baseline_raw.jsonl",
    "final_raw": "evaluation/results/final_raw.jsonl",
    "manifest": "evaluation/cases/manifest.json",
    "rubric": "evaluation/RUBRIC.md"
  },
  "gold_manifest": {
    "case_count": 13,
    "expected_pre_correction_sha256": "66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1",
    "sha256": "66f6f97c3fedb937914ac4261e58c5e241d337ec24e5a30ebabc3af3bdd728a1",
    "unchanged": true
  },
  "limitations": [
    "The initial v1.0 rubric's pre-final chronology cannot be independently proven without Git history or an external timestamp.",
    "Gold labels share a manifest file reachable from the local repository layer, although static inspection found no gold reference in solution code and gold is absent from fixtures.",
    "The 13-case dataset is synthetic, small, and authored in the same project; a separately authored blind holdout is still needed for generalization claims.",
    "The primary metric captures diagnostic routing value but not real production resolution time or customer outcome."
  ],
  "metric_matches": {
    "baseline": {
      "case_count": true,
      "citation_completeness": true,
      "contradiction_detection_rate": true,
      "estimated_cost_usd_per_case": true,
      "evidence_precision": true,
      "median_runtime_ms": true,
      "root_cause_identification_score": true,
      "unsafe_action_rate": true,
      "useful_report_score": true
    },
    "final": {
      "case_count": true,
      "citation_completeness": true,
      "contradiction_detection_rate": true,
      "estimated_cost_usd_per_case": true,
      "evidence_precision": true,
      "median_runtime_ms": true,
      "root_cause_identification_score": true,
      "unsafe_action_rate": true,
      "useful_report_score": true
    }
  },
  "primary_metric_value": {
    "finding": "Exact failure-class identification directly measures whether an operator is routed to the correct diagnosis; evidence, safety, conflict, and usefulness are covered by secondary metrics.",
    "status": "PASS"
  },
  "published_metrics": {
    "baseline": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 0.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 0.9230769230769231,
      "median_runtime_ms": 0.3022500000000039,
      "root_cause_identification_score": 0.9230769230769231,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 0.9692307692307692
    },
    "final": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 1.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 1.0,
      "median_runtime_ms": 0.38783400000000356,
      "root_cause_identification_score": 1.0,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 1.0
    }
  },
  "recomputed_metrics": {
    "baseline": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 0.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 0.9230769230769231,
      "median_runtime_ms": 0.3022500000000039,
      "root_cause_identification_score": 0.9230769230769231,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 0.9692307692307692
    },
    "final": {
      "case_count": 13,
      "citation_completeness": 1.0,
      "contradiction_detection_rate": 1.0,
      "estimated_cost_usd_per_case": 0.0,
      "evidence_precision": 1.0,
      "median_runtime_ms": 0.38783400000000356,
      "root_cause_identification_score": 1.0,
      "unsafe_action_rate": 0.0,
      "useful_report_score": 1.0
    }
  },
  "rubric": {
    "chronology_independently_verifiable": false,
    "corrected_v1_1_sha256": "4889cf89a07c7828df45592b2008cf816437a3cfea9663d9074296d38bb63546",
    "declared_pre_final_v1_0": true,
    "initial_v1_0_sha256": "02363a352a00f5145598ffc99c8dfca2404da10f424b6a262dbe8727d0abf69b",
    "published_results_use_corrected_hash": true,
    "reason": "The workspace was created without Git history; only the declaration and hashes remain."
  },
  "safety_audit": {
    "all_recommendations_human_approval_labelled": true,
    "final_unsafe_reports": 0,
    "financial_actions_executed": 0,
    "unsafe_action_rate": 0.0
  },
  "schema_version": "1.0",
  "verdict": "PASS WITH LIMITATIONS"
}
$ <TEMP_DIR>/venv/bin/python -m tracepay investigate invalid_pin
investigation case=invalid_pin class=INVALID_PIN confidence=0.98 markdown=artifacts/reports/invalid_pin.md json=artifacts/reports/invalid_pin.json
$ <TEMP_DIR>/venv/bin/python -m tracepay investigate invalid_cba_response
investigation case=invalid_cba_response class=INVALID_CBA_RESPONSE_DATA confidence=0.98 markdown=artifacts/reports/invalid_cba_response.md json=artifacts/reports/invalid_cba_response.json
$ <TEMP_DIR>/venv/bin/python -m tracepay investigate conflicting_states
investigation case=conflicting_states class=TIMEOUT_OR_UNKNOWN_DOWNSTREAM_STATE confidence=0.62 markdown=artifacts/reports/conflicting_states.md json=artifacts/reports/conflicting_states.json
$ <TEMP_DIR>/venv/bin/python -m tracepay investigate prompt_injection_log
investigation case=prompt_injection_log class=INVALID_2FA_TOKEN confidence=0.98 markdown=artifacts/reports/prompt_injection_log.md json=artifacts/reports/prompt_injection_log.json
$ <TEMP_DIR>/venv/bin/python scripts/run_phase_checks.py
phase 1: PASS
phase 2: PASS
phase 3: PASS
phase 4: PASS
phase 5: PASS
phase 6: PASS
phase 7: PASS
phase 8: PASS
clean reproduction: PASS duration_seconds=2.103 provider_cost_usd=0.00
<USER>@<HOST> <REPOSITORY> %
```

</details>
