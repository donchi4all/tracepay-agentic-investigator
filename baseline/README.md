# Fair baseline

The baseline is implemented in `src/tracepay/baseline.py`. It receives the same case fixture and uses the same collector/redaction layer as the final solution, then scans sanitized payloads with a fixed ordered keyword list and emits a fixed report contract.

This is a reasonable small support automation: it recognizes explicit codes, cites matching records, costs nothing, and never takes action. It cannot distinguish structural fields from free-form log prose, reconcile conflicting component states, or verify claims. Those limitations are measured rather than asserted.

Run one case with `make run-baseline CASE=invalid_pin` and the frozen set with `make evaluate-baseline`.

